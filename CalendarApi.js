const fs = require('fs');
const readline = require('readline');
const {google} = require('googleapis');

const TOKEN_PATH = 'token.json';
const oAuth2Client = new google.auth.OAuth2();
console.log(oAuth2Client)
console.log("----------------------------")
token = JSON.parse(fs.readFileSync(TOKEN_PATH, (err, token) => {
   return token
}))

oAuth2Client.setCredentials(token);
console.log(oAuth2Client)

// fs.readFile(TOKEN_PATH, (err, token) => {
//     if (err) return getAccessToken(oAuth2Client, callback);
//     oAuth2Client.setCredentials(JSON.parse(token));
//     callback(oAuth2Client);
//   });
// }