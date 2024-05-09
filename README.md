# AWS Advertisement Website Backend

The objective of this project is to design and implement the backend of an advertisement website using AWS and Serverless. This project has been developed as part of the Data Architecture and Engineering master's program at Datahack. 

## Implemented Requirements

The following requirements have been implemented:

- **Listing Ads**: Implementation of a API endpoint to list all ads registered in the database.
- **View Ad Details**: Creation of a API endpoint to view the details of a specific ad.
- **Publishing Ads**: Development of a API endpoint to publish a new text advert.
- **Chat/Comments Feature**: Integration of a chat/comments system associated with each ad. Source code for the chat: https://github.com/sergiokhayyat/simple-chat/tree/master

**Focus Areas:**

- **Cost Minimization**: Emphasis on minimizing operating costs, particularly during idle periods or when there are no active users. This includes consideration of both service costs and human resource costs.
- **Serverless Technologies**: Special attention has been given to leveraging serverless technologies to achieve the project's objectives efficiently.

## Deployment manual

To deploy this serverless project consisting of a `serverless.yml` file and a `handler.py` file, follow these steps:

### Prerrequisites

1. **Install Serverless Framework**: Ensure that you have Serverless Framework installed on your local machine. You can install it globally via npm by running the command:
   ```
   npm install -g serverless
   ```

2. Make sure to have your AWS credentials properly configured on your local machine so that Serverless Framework can interact with your AWS account during the deployment process. For more information, please refer to: https://www.serverless.com/framework/docs/getting-started

3. **Configure the `serverless.yml` File**: Ensure that your `serverless.yml` file is properly configured with the definition of your service, including Lambda functions, events, AWS resources, etc.

### Deployment

1. **Deploy the Service**: In your terminal, navigate to the root directory of your project and run the following command to deploy your service:
   ```
   serverless deploy
   ```

   This will initiate the deployment process of your service according to the configuration defined in the `serverless.yml` file.

2. **Monitor the Deployment**: Once the deployment is underway, Serverless Framework will display progress in the terminal, including created resources and any potential errors. Make sure to review any error messages and take necessary actions if something goes wrong.

3. **Verify the Deployment**: Once the deployment is complete, you can verify that your service has been deployed successfully by accessing the AWS console or using the AWS CLI to inspect the created resources.

