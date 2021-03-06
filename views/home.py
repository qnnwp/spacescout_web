from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
import oauth2
import simplejson as json
from django.utils.datastructures import SortedDict


def HomeView(request):
    # Default to zooming in on the UW Seattle campus if no default location is set
    if hasattr(settings, 'SS_DEFAULT_LOCATION'):
        loc = settings.SS_LOCATIONS[settings.SS_DEFAULT_LOCATION]
        center_latitude = loc['CENTER_LATITUDE']
        center_longitude = loc['CENTER_LONGITUDE']
        zoom_level = loc['ZOOM_LEVEL']
    else:
        center_latitude = '47.655003'
        center_longitude = '-122.306864'
        zoom_level = '15'

    search_args = {
        'center_latitude': center_latitude,
        'center_longitude': center_longitude,
        'open_now': '1',
        'distance': '500',
    }

    for key in request.GET:
        search_args[key] = request.GET[key]

    consumer = oauth2.Consumer(key=settings.SS_WEB_OAUTH_KEY, secret=settings.SS_WEB_OAUTH_SECRET)
    client = oauth2.Client(consumer)

    locations = settings.SS_LOCATIONS
    buildings = json.loads(get_building_json(client))

    # This could probably be a template tag, but didn't seem worth it for one-time use
    buildingdict = SortedDict()
    for building in buildings:
        if not building[0] in buildingdict.keys():  # building[0] is the first letter of the string
            buildingdict[building[0]] = []

        buildingdict[building[0]].append(building)

    # See if django-compressor is being used to precompile less
    if settings.COMPRESS_ENABLED:
        less_not_compiled = False
    else:
        less_not_compiled = True

    # See if there is a Google Analytics web property id
    try:
        ga_tracking_id = settings.GA_TRACKING_ID
    except:
        ga_tracking_id = None

    return render_to_response('app.html', {
        'center_latitude': center_latitude,
        'center_longitude': center_longitude,
        'zoom_level': zoom_level,
        'locations': locations,
        'buildingdict': buildingdict,
        'is_mobile': request.MOBILE,
        'less_not_compiled': less_not_compiled,
        'ga_tracking_id': ga_tracking_id,
    }, context_instance=RequestContext(request))


def get_building_json(client):
    url = "{0}/api/v1/buildings".format(settings.SS_WEB_SERVER_HOST)
    resp, content = client.request(url, 'GET')

    if resp.status == 200:
        return content

    return '[]'
