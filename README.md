# Github issues

A script to extract issues associated to a project V2 (new projects) from Github. The result will be a csv, issues.csv.

## How to adapt it to your project

You need:

- A github token : github/settings/Developpers settings/Personal access tokens/Tokens(classics)

- The project number: https://github.com/orgs/streamroot/projects/<the_number>

- The project id

To discover projects in the organization and find your id, execute:

POST https://api.github.com/graphql

body: 
``{organization(login: "streamroot") {projectsV2(first: 20) {nodes {id title}}}} ``


