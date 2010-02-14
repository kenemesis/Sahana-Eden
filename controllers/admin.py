# -*- coding: utf-8 -*-
import cPickle as pickle
import csv
from gluon.admin import *
from gluon.fileutils import listdir

module = 'admin'
# Current Module (for sidebar title)
module_name = db(db.s3_module.name==module).select().first().name_nice
# Options Menu (available in all Functions' Views)
# - can Insert/Delete items from default menus within a function, if required.
response.menu_options = admin_menu_options

# S3 framework functions
def index():
    "Module's Home Page"
    return dict(module_name=module_name)

@auth.requires_membership('Administrator')
def setting():
    "RESTlike CRUD controller"
    s3.crud_strings.setting.title_update = T('Edit Settings')
    s3.crud_strings.setting.msg_record_modified = T('Settings updated')
    s3.crud_strings.setting.label_list_button = None
    #crud.settings.update_next = URL(r=request, args=['update', 1])
    return shn_rest_controller('s3', 'setting', deletable=False, listadd=False, onvalidation=lambda form: theme_check(form), onaccept=lambda form: theme_apply(form))

@auth.requires_membership('Administrator')
def theme():
    "RESTlike CRUD controller"
    resource = 'theme'
    table = module + '_' + resource

    # Model options
    db[table].name.label = T('Name')
    db[table].name.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, '%s.name' % table)]
    db[table].name.comment = SPAN("*", _class="req")
    db[table].logo.label = T('Logo')
    db[table].logo.comment = A(SPAN("[Help]"), _class="tooltip", _title=T("Logo|Name of the file (& optional sub-path) located in static which should be used for the top-left image."))
    #db[table].header_background.label = T('Header Background')
    #db[table].header_background.comment = A(SPAN("[Help]"), _class="tooltip", _title=T("Header Background|Name of the file (& optional sub-path) located in static which should be used for the background of the header."))
    db[table].footer.label = T('Footer')
    db[table].footer.comment = A(SPAN("[Help]"), _class="tooltip", _title=T("Footer|Name of the file (& optional sub-path) located in views which should be used for footer."))
    db[table].text_direction.label = T('Text Direction')
    db[table].text_direction.requires = IS_IN_SET({'ltr':T('Left-to-Right'), 'rtl':T('Right-to-Left')})
    db[table].text_direction.comment = A(SPAN("[Help]"), _class="tooltip", _title=T("Text Direction|Whilst most languages are read from Left-to-Right, Arabic, Hebrew & Farsi go from Right-to-Left."))
    db[table].col_background.label = T('Background Colour')
    db[table].col_background.requires = IS_HTML_COLOUR()
    db[table].col_txt.label = T('Text Colour for Text blocks')
    db[table].col_txt.requires = IS_HTML_COLOUR()
    db[table].col_txt_background.label = T('Background Colour for Text blocks')
    db[table].col_txt_background.requires = IS_HTML_COLOUR()
    db[table].col_txt_border.label = T('Border Colour for Text blocks')
    db[table].col_txt_border.requires = IS_HTML_COLOUR()
    db[table].col_txt_underline.label = T('Colour for Underline of Subheadings')
    db[table].col_txt_underline.requires = IS_HTML_COLOUR()
    db[table].col_menu.label = T('Colour of dropdown menus')
    db[table].col_menu.requires = IS_HTML_COLOUR()
    db[table].col_highlight.label = T('Colour of selected menu items')
    db[table].col_highlight.requires = IS_HTML_COLOUR()
    db[table].col_input.label = T('Colour of selected Input fields')
    db[table].col_input.requires = IS_HTML_COLOUR()
    db[table].col_border_btn_out.label = T('Colour of bottom of Buttons when not pressed')
    db[table].col_border_btn_out.requires = IS_HTML_COLOUR()
    db[table].col_border_btn_in.label = T('Colour of bottom of Buttons when pressed')
    db[table].col_border_btn_in.requires = IS_HTML_COLOUR()
    db[table].col_btn_hover.label = T('Colour of Buttons when hovering')
    db[table].col_btn_hover.requires = IS_HTML_COLOUR()

    # CRUD Strings
    ADD_THEME = T('Add Theme')
    LIST_THEMES = T('List Themes')
    s3.crud_strings[resource] = Storage(
        title_create = ADD_THEME,
        title_display = T('Theme Details'),
        title_list = LIST_THEMES,
        title_update = T('Edit Theme'),
        title_search = T('Search Themes'),
        subtitle_create = T('Add New Theme'),
        subtitle_list = T('Themes'),
        label_list_button = LIST_THEMES,
        label_create_button = ADD_THEME,
        msg_record_created = T('Theme added'),
        msg_record_modified = T('Theme updated'),
        msg_record_deleted = T('Theme deleted'),
        msg_list_empty = T('No Themes currently defined'))

    return shn_rest_controller(module, resource, list_fields=['id', 'name', 'logo', 'footer', 'col_background'], onvalidation=lambda form: theme_check(form))

def theme_apply(form):
    "Apply the Theme specified by Form"
    if form.vars.theme:
        # Valid form
        # Relevant paths
        template = os.path.join(request.folder, 'static', 'styles', 'S3', 'template.css')
        tmp_folder = os.path.join(request.folder, 'static', 'scripts', 'tools')
        out_file = os.path.join(request.folder, 'static', 'styles', 'S3', 'sahana.css')
        out_file2 = os.path.join(request.folder, 'static', 'styles', 'S3', 'sahana.min.css')
        # Check permissions
        if not os.access(template, os.R_OK):
            session.error = T('Template file %s not readable - unable to apply theme!' % template)
            redirect(URL(r=request, args=request.args))
        if not os.access(tmp_folder, os.W_OK):
            session.error = T('Temp folder %s not writable - unable to apply theme!' % tmp_folder)
            redirect(URL(r=request, args=request.args))
        if not os.access(out_file, os.W_OK):
            session.error = T('CSS file %s not writable - unable to apply theme!' % out_file)
            redirect(URL(r=request, args=request.args))
        if not os.access(out_file2, os.W_OK):
            session.error = T('CSS file %s not writable - unable to apply theme!' % out_file2)
            redirect(URL(r=request, args=request.args))
        # Read in Template
        inpfile = open(template, 'r')
        lines = inpfile.readlines()
        inpfile.close()
        # Read settings from Database
        theme = db(db.admin_theme.id == form.vars.theme).select().first()
        default_theme = db(db.admin_theme.id == 1).select().first()
        if theme.logo:
            logo = theme.logo
        else:
            logo = default_theme.logo
        #if theme.header_background:
        #    header_background = theme.header_background
        #else:
        #    header_background = default_theme.header_background
        if theme.text_direction:
            text_direction = theme.text_direction
        else:
            text_direction = 'ltr'
        # Write out CSS
        ofile = open(out_file, 'w')
        for line in lines:
            line = line.replace("YOURLOGOHERE", logo)
            #line = line.replace("HEADERBACKGROUND", header_background )
            line = line.replace("TEXT_DIRECTION", text_direction)
            # Iterate through Colours
            for key in theme.keys():
                if key[:4] == 'col_':
                    if theme[key]:
                        line = line.replace(key, theme[key])
                    else:
                        line = line.replace(key, default_theme[key])
            ofile.write(line)
        ofile.close()

        # Minify
        from subprocess import PIPE, check_call
        currentdir = os.getcwd()
        os.chdir(os.path.join(currentdir, request.folder, 'static', 'scripts', 'tools'))
        import sys
        # If started as a services os.sys.executable is no longer python on
        # windows.
        if ("win" in sys.platform):
            pythonpath = os.path.join(sys.prefix, 'python.exe')
        else:
            pythonpath = os.sys.executable
        try:
            proc = check_call([pythonpath, 'build.sahana.py', 'CSS', 'NOGIS'], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        except:
            session.error = T('Error encountered while applying the theme.')
            redirect(URL(r=request, args=request.args))
        os.chdir(currentdir)

        # Don't do standard redirect to List view as we only want this option available
        redirect(URL(r=request, args=['update', 1]))
    else:
        session.error = INVALIDREQUEST
        redirect(URL(r=request))

def theme_check(form):
    "Check the Theme has valid files available"
    # Check which form we're called by
    if form.vars.theme:
        # Called from Settings
        theme = db(db.admin_theme.id == form.vars.theme).select().first()
        logo = theme.logo
        #header_background = theme.header_background
        footer = theme.footer
    elif form.vars.logo and form.vars.footer:
        # Called from Theme
        logo = form.vars.logo
        #header_background = form.vars.header_background
        footer = form.vars.footer
    else:
        session.error = INVALIDREQUEST
        redirect(URL(r=request))
    _logo = os.path.join(request.folder, 'static', logo)
    #_header_background = os.path.join(request.folder, 'static', header_background)
    _footer = os.path.join(request.folder, 'views', footer)
    if not os.access(_logo, os.R_OK):
        form.errors['logo'] = T('Logo file %s missing!' % logo)
        return
    #if not os.access(_header_background, os.R_OK):
    #    form.errors['header_background'] = T('Header background file %s missing!' % logo)
    #    return
    if not os.access(_footer, os.R_OK):
        form.errors['footer'] = T('Footer file %s missing!' % footer)
        return
    # Validation passed
    return

@auth.requires_membership('Administrator')
def user():
    "RESTlike CRUD controller"
    module = 'auth'
    resource = 'user'
    table = module + '_' + resource

    # Model options

    # CRUD Strings
    ADD_USER = T('Add User')
    LIST_USERS = T('List Users')
    s3.crud_strings[table] = Storage(
        title_create = ADD_USER,
        title_display = T('User Details'),
        title_list = LIST_USERS,
        title_update = T('Edit User'),
        title_search = T('Search Users'),
        subtitle_create = T('Add New User'),
        subtitle_list = T('Users'),
        label_list_button = LIST_USERS,
        label_create_button = ADD_USER,
        msg_record_created = T('User added'),
        msg_record_modified = T('User updated'),
        msg_record_deleted = T('User deleted'),
        msg_list_empty = T('No Users currently registered'))

    onvalidation = onaccept = None
    # Add users to Person Registry & 'Authenticated' role
    crud.settings.create_onaccept = lambda form: auth.shn_register(form)
    # Send an email to user if their account is approved (moved from 'pending' to 'blank'(i.e. enabled))
    if len(request.args) and request.args[0] == 'update':
        onvalidation = lambda form: user_approve(form)
    # Allow the ability for admin to Disable logins
    db.auth_user.registration_key.writable = True
    db.auth_user.registration_key.readable = True
    db.auth_user.registration_key.label = T('Disabled?')
    db.auth_user.registration_key.requires = IS_NULL_OR(IS_IN_SET(['disabled', 'pending']))

    return shn_rest_controller(module, resource, main='first_name', onvalidation=onvalidation, onaccept=onaccept)

def user_approve(form):
    "Send an email to user if their account is approved (moved from 'pending' to 'blank'(i.e. enabled))"
    if form.vars.registration_key:
        # Now non-blank
        return
    else:
        # Now blank - lookup old value
        status = db(db.auth_user.id == request.vars.id).select()[0].registration_key
        if status == 'pending':
            # Send email to user confirming that they are now able to login
            if not auth.settings.mailer or \
                   not auth.settings.mailer.send(to=form.vars.email,
                        subject=s3.messages.confirmation_email_subject,
                        message=s3.messages.confirmation_email):
                    session.warning = auth.messages.unable_send_email
                    return
        else:
            return

@auth.requires_membership('Administrator')
def group():
    "RESTlike CRUD controller"
    module = 'auth'
    resource = 'group'
    table = module + '_' + resource

    # Model options

    # CRUD Strings
    ADD_ROLE = T('Add Role')
    LIST_ROLES = T('List Roles')
    s3.crud_strings[table] = Storage(
        title_create = ADD_ROLE,
        title_display = T('Role Details'),
        title_list = LIST_ROLES,
        title_update = T('Edit Role'),
        title_search = T('Search Roles'),
        subtitle_create = T('Add New Role'),
        subtitle_list = T('Roles'),
        label_list_button = LIST_ROLES,
        label_create_button = ADD_ROLE,
        msg_record_created = T('Role added'),
        msg_record_modified = T('Role updated'),
        msg_record_deleted = T('Role deleted'),
        msg_list_empty = T('No Roles currently defined'))

    return shn_rest_controller(module, resource, main='role')

# Unused as poor UI
@auth.requires_membership('Administrator')
def membership():
    "RESTlike CRUD controller"
    module = 'auth'
    resource = 'membership'
    table = module + '_' + resource

    # Model options

    # CRUD Strings
    table = 'auth_membership'
    ADD_MEMBERSHIP = T('Add Membership')
    LIST_MEMBERSHIPS = T('List Memberships')
    s3.crud_strings[table] = Storage(
        title_create = ADD_MEMBERSHIP,
        title_display = T('Membership Details'),
        title_list = LIST_MEMBERSHIPS,
        title_update = T('Edit Membership'),
        title_search = T('Search Memberships'),
        subtitle_create = T('Add New Membership'),
        subtitle_list = T('Memberships'),
        label_list_button = LIST_MEMBERSHIPS,
        label_create_button = ADD_MEMBERSHIP,
        msg_record_created = T('Membership added'),
        msg_record_modified = T('Membership updated'),
        msg_record_deleted = T('Membership deleted'),
        msg_list_empty = T('No Memberships currently defined'))

    return shn_rest_controller(module, resource, main='user_id')

@auth.requires_membership('Administrator')
def users():
    "List/amend which users are in a Group"
    if len(request.args) == 0:
        session.error = T("Need to specify a role!")
        redirect(URL(r=request, f='group'))
    group = request.args(0)
    table = db.auth_membership
    query = table.group_id==group
    title = str(T('Role')) + ': ' + db.auth_group[group].role
    description = db.auth_group[group].description
    # Start building the Return
    output = dict(module_name=module_name, title=title, description=description, group=group)

    if auth.settings.username:
        username = 'username'
    else:
        username = 'email'

    # Audit
    crud.settings.create_onaccept = lambda form: shn_audit_create(form, module, 'membership', 'html')
    # Many<>Many selection (Deletable, no Quantity)
    item_list = []
    sqlrows = db(query).select()
    even = True
    for row in sqlrows:
        if even:
            theclass = "even"
            even = False
        else:
            theclass = "odd"
            even = True
        id = row.user_id
        item_first = db.auth_user[id].first_name
        item_second = db.auth_user[id].last_name
        item_description = db.auth_user[id][username]
        id_link = A(id, _href=URL(r=request, f='user', args=['read', id]))
        checkbox = INPUT(_type="checkbox", _value="on", _name=id, _class="remove_item")
        item_list.append(TR(TD(id_link), TD(item_first), TD(item_second), TD(item_description), TD(checkbox), _class=theclass))

    if auth.settings.username:
        username_label = T('Username')
    else:
        username_label = T('Email')
    table_header = THEAD(TR(TH('ID'), TH(T('First Name')), TH(T('Last Name')), TH(username_label), TH(T('Remove'))))
    table_footer = TFOOT(TR(TD(_colspan=4), TD(INPUT(_id='submit_delete_button', _type='submit', _value=T('Remove')))))
    items = DIV(FORM(TABLE(table_header, TBODY(item_list), table_footer, _id="table-container"), _name='custom', _method='post', _enctype='multipart/form-data', _action=URL(r=request, f='group_remove_users', args=[group])))

    subtitle = T("Users")
    crud.messages.submit_button = T('Add')
    crud.messages.record_created = T('Role Updated')
    form = crud.create(table, next=URL(r=request, args=[group]))
    addtitle = T("Add New User to Role")
    output.update(dict(subtitle=subtitle, items=items, addtitle=addtitle, form=form))
    return output

@auth.requires_membership('Administrator')
def group_remove_users():
    "Remove users from a group"
    if len(request.args) == 0:
        session.error = T("Need to specify a group!")
        redirect(URL(r=request, f='group'))
    group = request.args(0)
    table = db.auth_membership
    for var in request.vars:
        user = var
        query = (table.group_id==group) & (table.user_id==user)
        db(query).delete()
    # Audit
    #crud.settings.update_onaccept = lambda form: shn_audit_update(form, 'membership', 'html')
    session.flash = T("Users removed")
    redirect(URL(r=request, f='users', args=[group]))

@auth.requires_membership('Administrator')
def groups():
    "List/amend which groups a User is in"
    if len(request.args) == 0:
        session.error = T("Need to specify a user!")
        redirect(URL(r=request, f='user'))
    user = request.args(0)
    table = db.auth_membership
    query = table.user_id==user
    title = db.auth_user[user].first_name + ' ' + db.auth_user[user].last_name
    description = db.auth_user[user].email
    # Start building the Return
    output = dict(module_name=module_name, title=title, description=description, user=user)

    # Audit
    crud.settings.create_onaccept = lambda form: shn_audit_create(form, module, 'membership', 'html')
    # Many<>Many selection (Deletable, no Quantity)
    item_list = []
    sqlrows = db(query).select()
    even = True
    for row in sqlrows:
        if even:
            theclass = "even"
            even = False
        else:
            theclass = "odd"
            even = True
        id = row.group_id
        item_first = db.auth_group[id].role
        item_description = db.auth_group[id].description
        id_link = A(id, _href=URL(r=request, f='group', args=['read', id]))
        checkbox = INPUT(_type="checkbox", _value="on", _name=id, _class="remove_item")
        item_list.append(TR(TD(id_link), TD(item_first), TD(item_description), TD(checkbox), _class=theclass))

    table_header = THEAD(TR(TH('ID'), TH(T('Role')), TH(T('Description')), TH(T('Remove'))))
    table_footer = TFOOT(TR(TD(_colspan=3), TD(INPUT(_id='submit_delete_button', _type='submit', _value=T('Remove')))))
    items = DIV(FORM(TABLE(table_header, TBODY(item_list), table_footer, _id="table-container"), _name='custom', _method='post', _enctype='multipart/form-data', _action=URL(r=request, f='user_remove_groups', args=[user])))

    subtitle = T("Roles")
    crud.messages.submit_button = T('Add')
    crud.messages.record_created = T('User Updated')
    form = crud.create(table, next=URL(r=request, args=[user]))
    addtitle = T("Add New Role to User")
    output.update(dict(subtitle=subtitle, items=items, addtitle=addtitle, form=form))
    return output

@auth.requires_membership('Administrator')
def user_remove_groups():
    "Remove groups from a user"
    if len(request.args) == 0:
        session.error = T("Need to specify a user!")
        redirect(URL(r=request, f='user'))
    user = request.args(0)
    table = db.auth_membership
    for var in request.vars:
        group = var
        query = (table.group_id==group) & (table.user_id==user)
        db(query).delete()
    # Audit
    #crud.settings.update_onaccept = lambda form: shn_audit_update(form, 'membership', 'html')
    session.flash = T("Groups removed")
    redirect(URL(r=request, f='groups', args=[user]))

# Import Data
@auth.requires_membership('Administrator')
def import_data():
    "Import data via POST upload to CRUD controller."
    title = T('Import Data')
    crud.messages.submit_button = 'Upload'
    import_job_form = crud.create(db.admin_import_job)
    # Doesn't seem to be any proper way to tell the CRUD create form to post to
    # a different location!!!
    import_job_form.custom.begin.text = str(import_job_form.custom.begin).replace(
            'action=""',
            'action="%s"' % URL(r=request, f='import_job', args=['create']))
    return dict(module_name=module_name, title=title,
                import_job_form=import_job_form)

@auth.requires_membership('Administrator')
def import_csv():
    "Import CSV data via POST upload to Database."
    file = request.vars.multifile.file
    try:
        # Assumes that it is a concatenation of tables
        shn_import_csv(file)
        session.flash = T('Data uploaded')
    except Exception, e:
        session.error = T('Unable to parse CSV file!')
    redirect(URL(r=request, f='import_data'))

# Export Data
@auth.requires_login()
def export_data():
    "Export data via CRUD controller."
    title = T('Export Data')
    return dict(module_name=module_name, title=title)

@auth.requires_login()
def export_csv():
    "Export entire database as CSV"
    import StringIO
    output = StringIO.StringIO()

    db.export_to_csv_file(output)

    output.seek(0)
    import gluon.contenttype
    response.headers['Content-Type'] = gluon.contenttype.contenttype('.csv')
    filename = "%s_database.csv" % (request.env.server_name)
    response.headers['Content-disposition'] = "attachment; filename=%s" % filename
    return output.read()


# Unstructured Data Import
@auth.requires_membership('Administrator')
def import_job():
    "RESTlike CRUD controller to handle 'jobs' for importing unstructured data."
    # CRUD Strings
    module = 'admin'
    resource = 'import_job'
    table = '%s_%s' % (module, resource)
    jr = s3xrc.request(module, resource, request, session=session)
    CREATE_NEW_IMPORT_JOB = T('Create New Import Job')
    LIST_IMPORT_JOBS = ('List Import Jobs')
    s3.crud_strings[table] = Storage(
            title_create=CREATE_NEW_IMPORT_JOB,
            title_display=T('Import Job'),
            title_list=LIST_IMPORT_JOBS,
            title_update=T('Update Import Job'),
            subtitle_create=CREATE_NEW_IMPORT_JOB,
            subtitle_list=T('Import Jobs'),
            label_list_button=LIST_IMPORT_JOBS,
            label_create_button=T('Create Import Job'),
            msg_record_created=T('Import job created'),
            msg_list_empty=T('No import jobs')
    )

    if len(request.args) == 0:
        return _import_job_list(jr)
    action = request.args[0]
    if action == 'create':
        return _import_job_create(jr)
    if action == 'update':
        return _import_job_update(jr)

def _import_job_list(jr):
    return shn_list(jr, listadd=False)

def _import_job_create(jr):
    if jr.http != 'POST':
        redirect(jr.there())

    def process_new_file_and_redirect(form):
        filename = form.vars.source_file_newfilename
        filepath = os.path.join(request.folder, 'uploads', filename)
        query = jr.table.id==form.vars.id
        column_map = []
        model_fields = dict(map(
                lambda x:(x.lower(), x),
                get_matchable_fields(form.vars.module, form.vars.resource)))
        try:
            reader = csv.reader(open(filepath, 'r'))
            for line in reader:
                for col in line:
                    field = None
                    col_match = col.lower()
                    if col_match in model_fields:
                        # Explicit name match.
                        field = model_fields.pop(col_match)
                    if not field:
                        # Partial name patch.
                        for field_name in model_fields:
                            if col_match in field_name or field_name in col_match:
                                field = model_fields.pop(field_name)
                                break
                    column_map.append((col, field))
                break
            pickled_map = pickle.dumps(column_map, pickle.HIGHEST_PROTOCOL)
            db(query).update(column_map=pickled_map)
        except:
            db(query).update(status='failed')
        redirect(URL(r=request, f='import_job', args=['update', form.vars.id]))

    form = crud.create(jr.table, onaccept=process_new_file_and_redirect)
    response.flash = 'Form errors!'
    redirect(URL(r=request, f='import_data'))

def _import_job_update(jr):
    if len(request.args) < 2:
        redirect(jr.there())
    id = request.args[1]
    query = jr.table.id==id
    job = db(query).select()
    if not job:
        raise HTTP(404, body=json_message(False, 404, session.error))
    job = job[0]

    if jr.http == 'GET':
        output = _import_job_update_GET(jr, job)
    elif jr.http == 'POST':
        output = _import_job_update_POST(jr, job)
    else:
        raise HTTP(400, body=INVALIDREQUEST)

    title = '%s - %s' % (T('Input Job'), job.description)
    output.update(dict(module_name=module_name, title=title, job=job))
    response.view = 'admin/import_job_update.html'
    return output

def _import_job_update_GET(jr, job):
    table = db.admin_import_line
    query = table.import_job==job.id

    if job.status == 'new':
        try:
            job.column_map = pickle.loads(job.column_map)
        except pickle.UnpicklingError:
            job.column_map = []
        model_fields = get_matchable_fields(job.module, job.resource)
        return dict(model_fields=model_fields)

    if job.status == 'processing':
        num_lines = db(query).count()
        return dict(num_lines=num_lines, update_speed=60)

    if job.status in ['processed', 'failed', 'imported']:
        def _include_field(f):
            if f in ['import_job']:
                return False
            return table[f].readable

        fields = [table[f] for f in table.fields if _include_field(f)]
        headers = dict(map(lambda f: (str(f), f.label), fields))
        items = crud.select(
                db['admin_import_line'],
                query=query,
                fields=fields,
                headers=headers,
                truncate=48, _id='list', _class='display')
        response.extra_styles = ['admin/import_job.css']
        return dict(items=items)

    if job.status == 'import':
        query = (table.import_job==job.id) & (table.status=='imported')
        num_lines = db(query).count()
        return dict(num_lines=num_lines, update_speed=60)

    return {}

#      items = crud.select(table, query=query,
#            fields=fields,
#            orderby=orderby,
#            limitby=limitby,
#            headers=headers,
#            linkto=linkto,
#            truncate=48, _id='list', _class='display')

def _import_job_update_POST(jr, job):
    if job.status == 'new':
        # Update column map.
        try:
            column_map = pickle.loads(job.column_map)
        except pickle.UnpicklingError:
            column_map = []
        for key, value in request.vars.iteritems():
            if not key.startswith('column_map_'):
                continue
            try:
                idx = int(key.split('_')[-1])
            except ValueError:
                continue
            if value != 'None (Ignore)':
                column_map[idx] = (column_map[idx][0], value)
            else:
                column_map[idx] = (column_map[idx][0], None)
        jr.table[job.id] = dict(
                column_map=pickle.dumps(column_map, pickle.HIGHEST_PROTOCOL),
                status='processing')
        job.status = 'processing'

    if job.status == 'processed':
        query = db.admin_import_line.id
        for var, status in request.vars.iteritems():
            if not var.startswith('status_'):
                continue
            try:
                import_line_id = int(var.split('_')[-1])
            except ValueError:
                continue
            db(db.admin_import_line.id==import_line_id).update(status=status)
        jr.table[job.id] = dict(status='import')
        job.status = 'import'

    return _import_job_update_GET(jr, job)

def get_matchable_fields(module, resource):
    model_fields = getattr(db, '%s_%s' % (module, resource)).fields
    for name in ['created_on', 'modified_on', 'id', 'uuid', 'deleted']:
        model_fields.remove(name)
    model_fields.insert(0, 'None (Ignore)')
    return model_fields


# Functional Testing
def handleResults():
    """Process the POST data returned from Selenium TestRunner.
    The data is written out to 2 files.  The overall results are written to
    date-time-browserName-metadata.txt as a list of key: value, one per line.  The
    suiteTable and testTables are written to date-time-browserName-results.html.
    """

    if not request.vars.result:
        # No results
        return

    # Read in results
    result = request.vars.result
    totalTime = request.vars.totalTime
    numberOfSuccesses = request.vars.numTestPasses
    numberOfFailures = request.vars.numTestFailures
    numberOfCommandSuccesses = request.vars.numCommandPasses
    numberOfCommandFailures = request.vars.numCommandFailures
    numberOfCommandErrors = request.vars.numCommandErrors

    suiteTable = ''
    if request.vars.suite:
        suiteTable = request.vars.suite

    testTables = []
    testTableNum = 1
    while request.vars['testTable.%s' % testTableNum]:
        testTable = request.vars['testTable.%s' % testTableNum]
        testTables.append(testTable)
        testTableNum += 1
        try:
            request.vars['testTable.%s' % testTableNum]
            pass
        except:
            break

    # Unescape the HTML tables
    import urllib
    suiteTable = urllib.unquote(suiteTable)
    testTables = map(urllib.unquote, testTables)

    # We want to store results separately for each browser
    browserName = getBrowserName(request.env.http_user_agent)
    date = str(request.utcnow)[:-16]
    time = str(request.utcnow)[11:-10]
    time = time.replace(':','-')

    # Write out results
    outputDir = os.path.join(request.folder, 'static', 'selenium', 'results')
    metadataFile = '%s-%s-%s-metadata.txt' % (date, time, browserName)
    dataFile = '%s-%s-%s-results.html' % (date, time, browserName)

    #xmlText = '<selenium result="' + result + '" totalTime="' + totalTime + '" successes="' + numberOfCommandSuccesses + '" failures="' + numberOfCommandFailures + '" errors="' + numberOfCommandErrors + '" />'
    f = open(os.path.join(outputDir, metadataFile), 'w')
    for key in request.vars.keys():
        if 'testTable' in key or key in ['log','suite']:
            pass
        else:
            print >> f, '%s: %s' % (key, request.vars[key])
    f.close()

    f = open(os.path.join(outputDir, dataFile), 'w')
    print >> f, suiteTable
    for testTable in testTables:
        print >> f, '<br/><br/>'
        print >> f, testTable
    f.close()

    message = DIV(P('Results have been successfully posted to the server here:'),
        P(A(metadataFile, _href=URL(r=request, c='static', f='selenium', args=['results', metadataFile]))),
        P(A(dataFile, _href=URL(r=request, c='static', f='selenium', args=['results', dataFile]))))

    response.view = 'display.html'
    title = T('Test Results')
    return dict(module_name=module_name, title=title, item=message)

#Ticket Viewer functions Borrowed from admin application of web2py
@auth.requires_membership('Administrator')
def errors():
    """ Error handler """

    app = request.application

    for item in request.vars:
        if item[:7] == 'delete_':
            os.unlink(apath('%s/errors/%s' % (app, item[7:]), r=request))

    func = lambda p: os.stat(apath('%s/errors/%s' % (app, p), r=request)).st_mtime
    tickets = sorted(listdir(apath('%s/errors/' % app, r=request), '^\w.*'),
                     key=func,
                     reverse=True)

    return dict(app=app, tickets=tickets)

def make_link(path):
    """ Create a link from a path """
    tryFile = path.replace('\\', '/')

    if os.path.isabs(tryFile) and os.path.isfile(tryFile):
        (folder, filename) = os.path.split(tryFile)
        (base, ext) = os.path.splitext(filename)
        app = request.args[0]

        editable = {'controllers': '.py', 'models': '.py', 'views': '.html'}
        for key in editable.keys():
            check_extension = folder.endswith("%s/%s" % (app,key))
            if ext.lower() == editable[key] and check_extension:
                return A('"' + tryFile + '"',
                         _href=URL(r=request,
                         f='edit/%s/%s/%s' % (app, key, filename))).xml()
    return ''


def make_links(traceback):
    """ Make links using the given traceback """

    lwords = traceback.split('"')

    # Making the short circuit compatible with <= python2.4
    result = (len(lwords) != 0) and lwords[0] or ''

    i = 1

    while i < len(lwords):
        link = make_link(lwords[i])

        if link == '':
            result += '"' + lwords[i]
        else:
            result += link

            if i + 1 < len(lwords):
                result += lwords[i + 1]
                i = i + 1

        i = i + 1

    return result


class TRACEBACK(object):
    """ Generate the traceback """

    def __init__(self, text):
        """ TRACEBACK constructor """

        self.s = make_links(CODE(text).xml())

    def xml(self):
        """ Returns the xml """

        return self.s


##ticket viewing
@auth.requires_membership('Administrator')
def ticket():
    """ Ticket handler """

    if len(request.args) != 2:
        session.flash = T('invalid ticket')
        redirect(URL(r=request))

    app = request.args[0]
    ticket = request.args[1]
    e = RestrictedError()
    e.load(request, app, ticket)

    return dict(app=app,
                ticket=ticket,
                traceback=TRACEBACK(e.traceback),
                code=e.code,
                layer=e.layer)

