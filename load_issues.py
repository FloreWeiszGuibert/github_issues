import requests, json
import csv

auth_token = 'Bearer <token>'
project_id = 'PVT_kwDOAFLUEM4AGhcO'
project_number = '19'

def get_issues_search(cursor):
    search_start = 'search(type: ISSUE , query: "org:streamroot is:issue project:streamroot/{}", first: 100 '.format(project_number)
    if "" == cursor:
        return search_start +")"
    else:
        return search_start + ', after:"' + cursor + '"'+')'

def get_issues_query(cursor):
    requested_content = """
    {
        issueCount
        pageInfo {
        hasNextPage
        endCursor
        }
        edges {
        node {
            __typename
            ... on Issue {
            id
            title
            bodyText
            state
            resourcePath
            createdAt
            updatedAt
            milestone{
              title
            }
            labels(first:10){
                nodes{name}
            }
            projectItems(first:20){
                nodes{
                    ... on ProjectV2Item {
                        fieldValues(first:30) {
                            nodes {
                                ... on ProjectV2ItemFieldSingleSelectValue{
                                    name
                                    field {
                                        ... on ProjectV2SingleSelectField{
                                            name
                                        }
                                    }
                                    item {
                                        project{
                                            ... on ProjectV2{
                                                id
                                            }
                                        }
                                    }
                                }
                                ... on ProjectV2ItemFieldTextValue{
                                    text
                                    field {
                                        ... on ProjectV2Field{
                                            name
                                        }
                                    }
                                    item {
                                        project{
                                            ... on ProjectV2{
                                                id
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            }
        }
        }
    }
    """
    return '{' + get_issues_search(cursor) + requested_content + '}'


def run_graphql_query(query): 
    request = requests.post('https://api.github.com/graphql', json={'query': query}, 
    headers = {'content-type': 'application/vnd.github+json', 'Authorization': auth_token})
    if request.status_code == 200:
        return request.json()
    else:
        print("Query failed to run by returning code of {}. {}".format(request.status_code, query))
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

def readFields(edgesNode):
    result = json.loads('{}')
    projectItemNodes = edgesNode['projectItems']['nodes']
    for projectItemNode in projectItemNodes:
        fieldValues = projectItemNode['fieldValues']
        if fieldValues != None:
            fieldValuesNodes = fieldValues['nodes']
            for fieldValuesNode in fieldValuesNodes:
                if 'item' in fieldValuesNode:
                    project = fieldValuesNode['item']['project']['id']
                    if json.dumps(project).strip('"') == project_id:
                        value = ""
                        if 'name' in fieldValuesNode:
                            value = json.dumps(fieldValuesNode['name']).strip('"')
                        if 'text' in fieldValuesNode:
                            value = json.dumps(fieldValuesNode['text']).strip('"')
                        if 'field' in fieldValuesNode and 'name' in fieldValuesNode['field']:
                            name = json.dumps(fieldValuesNode['field']['name']).strip('"')
                            result[name] = value
    return json.dumps(result)

def readBodyText(node):
    res = node['bodyText']
    return repr(res)

def readLabels(node):
    res = node['labels']['nodes']
    return json.dumps(res)

def readMilestone(node):
    milestone = node['milestone']
    if milestone != None:
        return milestone['title']
    return ""

def writeIssues(issuewriter, edges):
    for item in edges:
        node = item['node']
        id = node['id']
        title = node['title']
        state = node['state']
        fields = readFields(node)
        resourcePath = node['resourcePath']
        labels = readLabels(node)
        milestone = readMilestone(node)
        bodyText = readBodyText(node)
        issuewriter.writerow([id, title, fields, resourcePath, labels, milestone, state, bodyText])

with open('issues.csv', 'w', newline='') as csvfile:
    issuewriter = csv.writer(csvfile, delimiter=';')
    has_next_page = True
    cursor = ""
    page = 1

    while has_next_page:
        response = run_graphql_query(get_issues_query(cursor))
        searchNode = response['data']['search']

        if 1 == page:
            print("Number of issues: "+str(searchNode['issueCount']))
            
        print("Page: "+str(page))
        page += 1

        has_next_page = searchNode['pageInfo']['hasNextPage']
        cursor = searchNode['pageInfo']['endCursor']
        edges = searchNode['edges']
        writeIssues(issuewriter, edges)
