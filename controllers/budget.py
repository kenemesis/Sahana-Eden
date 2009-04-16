module='budget'
# Current Module (for sidebar title)
module_name=db(db.s3_module.name==module).select()[0].name_nice
# List Modules (from which to build Menu of Modules)
modules=db(db.s3_module.enabled=='Yes').select(db.s3_module.ALL,orderby=db.s3_module.priority)
# List Options (from which to build Menu for this Module)
options=db(db['%s_menu_option' % module].enabled=='Yes').select(db['%s_menu_option' % module].ALL,orderby=db['%s_menu_option' % module].priority)

# S3 framework functions
def index():
    "Module's Home Page"
    return dict(module_name=module_name,modules=modules,options=options)

def open_option():
    "Select Option from Module Menu"
    id=request.vars.id
    options=db(db['%s_menu_option' % module].id==id).select()
    if not len(options):
        redirect(URL(r=request,f='index'))
    option=options[0].function
    redirect(URL(r=request,f=option))

def parameters():
    "Select which page to go to depending on login status"
    if auth.is_logged_in():
        redirect (URL(r=request,f='parameter',args=['update',1]))
    else:
        redirect (URL(r=request,f='parameter',args=['read',1]))
def parameter():
    "RESTlike CRUD controller"
    return shn_rest_controller(module,'parameter',deletable=False)
def item():
    "RESTlike CRUD controller"
    return shn_rest_controller(module,'item',main='code',list='table')
def kit():
    "RESTlike CRUD controller"
    return shn_rest_controller(module,'kit',main='code',list='table')
#def kit_item():
#    "RESTlike CRUD controller"
#    return shn_rest_controller(module,'kit_item',main='kit_id',list='table')
def kit_item():
    "Many to Many CRUD Controller"
    if len(request.args)==0:
        session.error = T("Need to specify a kit!")
        redirect(URL(r=request,f='kit'))
    kit=request.args[0]
    table=db['%s_kit_item' % module]
    table.kit_id.readable=False
    fields = [table[f] for f in table.fields if table[f].readable]
    headers={}
    for field in fields:
        # Use custom or prettified label
        headers[str(field)]=field.label
    query = table.kit_id==kit
    linkto = URL(r=request, f='item', args='read')
    id = 'item_id'
    list=crud.select(table,query=query,fields=fields,headers=headers,linkto=linkto,id=id)
    title=db.budget_kit[kit].code
    description=db.budget_kit[kit].description
    if auth.is_logged_in():
        crud.settings.submit_button='Add'
        # Calculate Totals for the Kit after Item is added
        crud.settings.create_onaccept = lambda form: totals(form)
        form=crud.create(table,next=URL(r=request,args=[kit]))
        addtitle=T("Add New Item to Kit")
        response.view='%s/kit_item_list_create.html' % module
        return dict(module_name=module_name,modules=modules,options=options,title=title,description=description,list=list,addtitle=addtitle,form=form,kit=kit)
    else:
        response.view='%s/kit_item_list.html' % module
        return dict(module_name=module_name,modules=modules,options=options,title=title,description=description,list=list)
def totals(form):
    "Calculate Totals for the Kit"
    kit_id=form.vars.kit_id
    items=db(db.budget_kit_item.kit_id==kit_id).select()
    total_unit_cost=0
    total_monthly_cost=0
    total_minute_cost=0
    total_megabyte_cost=0
    for item in items:
        total_unit_cost+=(db(db.budget_item.id==item.item_id).select()[0].unit_cost)*(db(db.budget_kit_item.id==kit_id).select()[0].quantity)
        total_monthly_cost+=(db(db.budget_item.id==item.item_id).select()[0].monthly_cost)*(db(db.budget_kit_item.id==kit_id).select()[0].quantity)
        total_minute_cost+=(db(db.budget_item.id==item.item_id).select()[0].minute_cost)*(db(db.budget_kit_item.id==kit_id).select()[0].quantity)
        total_megabyte_cost+=(db(db.budget_item.id==item.item_id).select()[0].megabyte_cost)*(db(db.budget_kit_item.id==kit_id).select()[0].quantity)
    db(db.budget_kit.id==kit_id).update(total_unit_cost=total_unit_cost,total_monthly_cost=total_monthly_cost,total_minute_cost=total_minute_cost,total_megabyte_cost=total_megabyte_cost)
def bundle():
    "RESTlike CRUD controller"
    return shn_rest_controller(module,'bundle')
def staff_type():
    "RESTlike CRUD controller"
    return shn_rest_controller(module,'staff_type')
def location():
    "RESTlike CRUD controller"
    return shn_rest_controller(module,'location',main='code')
def project():
    "RESTlike CRUD controller"
    return shn_rest_controller(module,'project',main='code',extra='title')
def budget():
    "RESTlike CRUD controller"
    return shn_rest_controller(module,'budget')
def budget_equipment():
    "RESTlike CRUD controller"
    return shn_rest_controller(module,'budget_equipment')
def budget_staff():
    "RESTlike CRUD controller"
    return shn_rest_controller(module,'budget_staff')
