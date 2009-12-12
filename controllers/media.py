﻿# -*- coding: utf-8 -*-

module = 'media'
# Current Module (for sidebar title)
module_name = db(db.s3_module.name==module).select()[0].name_nice
# Options Menu (available in all Functions' Views)
response.menu_options = [
    [T('Images'), False, URL(r=request, f='image')],
    [T('Metadata'), False, URL(r=request, f='metadata')],
    [T('Bulk Uploader'), False, URL(r=request, f='bulk_upload')]
]

# Web2Py Tools functions
def download():
    "Download a file."
    return response.download(request, db) 

# S3 framework functions
def index():
    "Module's Home Page"
    return dict(module_name=module_name)

def metadata():
    "RESTlike CRUD controller"
    resource = 'metadata'
    table = module + '_' + resource
    
    # Model options
    # used in multiple controllers, so in the model
    
    # CRUD Strings
    title_create = T('Add Metadata')
    title_display = T('Metadata Details')
    title_list = T('List Metadata')
    title_update = T('Edit Metadata')
    title_search = T('Search Metadata')
    subtitle_create = T('Add New Metadata')
    subtitle_list = T('Metadata')
    label_list_button = T('List Metadata')
    label_create_button = ADD_METADATA
    msg_record_created = T('Metadata added')
    msg_record_modified = T('Metadata updated')
    msg_record_deleted = T('Metadata deleted')
    msg_list_empty = T('No Metadata currently defined')
    s3.crud_strings[table] = Storage(title_create=title_create,title_display=title_display,title_list=title_list,title_update=title_update,title_search=title_search,subtitle_create=subtitle_create,subtitle_list=subtitle_list,label_list_button=label_list_button,label_create_button=label_create_button,msg_record_created=msg_record_created,msg_record_modified=msg_record_modified,msg_record_deleted=msg_record_deleted,msg_list_empty=msg_list_empty)
    
    return shn_rest_controller(module, resource)

def image():
    "RESTlike CRUD controller"
    resource = 'image'
    table = module + '_' + resource
    
    # Model options
    # used in multiple controllers, so in the model

    # CRUD Strings
    title_create = T('Add Image')
    title_display = T('Image Details')
    title_list = T('List Image')
    title_update = T('Edit Image')
    title_search = T('Search Image')
    subtitle_create = T('Add New Image')
    subtitle_list = T('Image')
    label_list_button = T('List Image')
    label_create_button = ADD_IMAGE
    msg_record_created = T('Image added')
    msg_record_modified = T('Image updated')
    msg_record_deleted = T('Image deleted')
    msg_list_empty = T('No Image currently defined')
    s3.crud_strings[table] = Storage(title_create=title_create,title_display=title_display,title_list=title_list,title_update=title_update,title_search=title_search,subtitle_create=subtitle_create,subtitle_list=subtitle_list,label_list_button=label_list_button,label_create_button=label_create_button,msg_record_created=msg_record_created,msg_record_modified=msg_record_modified,msg_record_deleted=msg_record_deleted,msg_list_empty=msg_list_empty)
    
    return shn_rest_controller(module, resource)

def bulk_upload():
    """
    Custom view to allow bulk uploading of photos which are made into GIS Features.
    Lat/Lon can be pulled from an associated GPX track with timestamp correlation.
    """
    
    crud.messages.submit_button = T('Upload')

    form = crud.create(db.media_metadata)
    
    gpx_tracks = OptionsWidget()
    gpx_widget = gpx_tracks.widget(track_id.track_id, track_id.track_id.default, _id='gis_layer_gpx_track_id')
    gpx_label = track_id.track_id.label
    gpx_comment = track_id.track_id.comment
    
    feature_group = OptionsWidget()
    fg_widget = feature_group.widget(feature_group_id.feature_group_id, feature_group_id.feature_group_id.default, _id='gis_location_to_feature_group_feature_group_id')
    fg_label = feature_group_id.feature_group_id.label
    fg_comment = feature_group_id.feature_group_id.comment
    
    response.title = T('Bulk Uploader')
    
    return dict(form=form, gpx_widget=gpx_widget, gpx_label=gpx_label, gpx_comment=gpx_comment, fg_widget=fg_widget, fg_label=fg_label, fg_comment=fg_comment, IMAGE_EXTENSIONS=IMAGE_EXTENSIONS)
 
def upload_bulk():
    "Receive the Uploaded data from bulk_upload()"
    # Is there a GPX track to correlate timestamps with?
    track_id = form.vars.track_id
    # Is there a Feature Group to add Features to?
    feature_group_id = form.vars.feature_group_id
    # Collect default metadata
    description = form.vars.description
    person_id = form.vars.person_id
    source = form.vars.source
    accuracy = form.vars.accuracy
    sensitivity = form.vars.sensitivity
    event_time = form.vars.event_time
    expiry_time = form.vars.expiry_time
    url = form.vars.url
    
    # Insert initial metadata
    metadata_id = db.media_metadata.insert(description=description, person_id=person_id, source=source, accuracy=accuracy, sensitivity=sensitivity, event_time=event_time, expiry_time=expiry_time)

    # Extract timestamps from GPX file
    # ToDo: Parse using lxml?
	
    # Receive file
    location_id
    image
                
    image_filename = db.insert()
    
    # Read EXIF Info from file
    exec('import applications.%s.modules.EXIF as EXIF' % request.application)
    # Faster for Production (where app-name won't change):
    #import applications.sahana.modules.EXIF as EXIF

    f = open(file_image, 'rb')
    tags = EXIF.process_file(f, details=False)
    for key in tags.keys():
        # Timestamp
        if key[tag] == '':
            timestamp = key[tag]
        # ToDo: LatLon
        # ToDo: Metadata

    # Add iamge to database
    image_id = db.media_image.insert()
    
    return json_message(True, '200', "Files Processed.")

def upload(module, resource, table, tablename, onvalidation=None, onaccept=None):
    # Receive file ( from import_url() )
    record = Storage()
    
    for var in request.vars:
        
        # Skip the Representation
        if var == 'format':
            continue
        elif var == 'uuid':
            uuid = request.vars[var]
        elif table[var].type == 'upload':
            # Handle file uploads (copied from gluon/sqlhtml.py)
            field = table[var]
            fieldname = var
            f = request.vars[fieldname]
            fd = fieldname + '__delete'
            if f == '' or f == None:
                #if request.vars.get(fd, False) or not self.record:
                if request.vars.get(fd, False):
                    record[fieldname] = ''
                else:
                    #record[fieldname] = self.record[fieldname]
                    pass
            elif hasattr(f,'file'):
                (source_file, original_filename) = (f.file, f.filename)
            elif isinstance(f, (str, unicode)):
                ### do not know why this happens, it should not
                (source_file, original_filename) = \
                    (cStringIO.StringIO(f), 'file.txt')
            newfilename = field.store(source_file, original_filename)
            request.vars['%s_newfilename' % fieldname] = record[fieldname] = newfilename 
            if field.uploadfield and not field.uploadfield==True:
                record[field.uploadfield] = source_file.read()
        else:
            record[var] = request.vars[var]

    # Validate record
    for var in record:
        if var in table.fields:
            value = record[var]
            (value, error) = s3xrc.xml.validate(table, original, var, value)
        else:
            # Shall we just ignore non-existent fields?
            # del record[var]
            error = "Invalid field name."
        if error:
            raise HTTP(400, body=json_message(False, 400, var + " invalid: " + error))
        else:
            record[var] = value

    form = Storage()
    form.method = method
    form.vars = record

    # Onvalidation callback
    if onvalidation:
        onvalidation(form)

    # Create/update record
    try:
        if jr.component:
            record[jr.fkey]=jr.record[jr.pkey]
        if method == 'create':
            id = table.insert(**dict(record))
            if id:
                error = 201
                item = json_message(True, error, "Created as " + str(jr.other(method=None, record_id=id)))
                form.vars.id = id
                if onaccept:
                    onaccept(form)
            else:
                error = 403
                item = json_message(False, error, "Could not create record!")

        elif method == 'update':
            result = db(table.uuid==uuid).update(**dict(record))
            if result:
                error = 200
                item = json_message(True, error, "Record updated.")
                form.vars.id = original.id
                if onaccept:
                    onaccept(form)
            else:
                error = 403
                item = json_message(False, error, "Could not update record!")

        else:
            error = 501
            item = json_message(False, error, "Unsupported Method!")
    except:
        error = 400
        item = json_message(False, error, "Invalid request!")

    raise HTTP(error, body=item)