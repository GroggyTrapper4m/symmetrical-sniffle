### Azure Function to check Open Source Libraries
Security comments on legacy libraries with good ol' Azure's help!

### Background 
Azure Function application that looks at the current libraries used within a python project and comparing them against
vulnerabilities found in the [pypi.org](http://pypi.org) package information.

This project looks for the requirements listing and with conjunction with [Azure Logic Apps](https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-overview) sends a message on a predetermined basis through an SMTP server to necessary users.

Since this is using using GitHub, Bitbucket could work as well.

More information about Azure Functions can be found online at [AZ Functions](https://azure.microsoft.com/en-us/products/functions/)

### Envionment values
`VCS_Token` - More information can be found [online](https://support.atlassian.com/bitbucket-cloud/docs/repository-access-tokens/)

`REPOSITORY_NAME` - name of the respository you want to check.

`BRANCH_NAME` - name in the branch you want to look into.

#### Breakdown of Libraries used

`GHFunctionProject > requirements.txt` - The necessary libraries for the Azure function to properly run.
`requirements.txt` - The example libraries this project is checking against. 

### Helpful tools for local work
<ol>
<li>[Azurite VS Code Extension] - (https://marketplace.visualstudio.com/items?itemName=Azurite.azurite) - Local storage to run function. </li>
<li>[Azure Functions VS Code Extension] - (https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions)</li>
</ol>