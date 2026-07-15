const expectedUsers = 2500;
const domain = "example.com";
const url = "https://example.com";
const dnsInfo = {
  "status": 0,
  "records": [
    {
      "type": 1,
      "data": "104.20.23.154",
      "ttl": 300
    },
    {
      "type": 1,
      "data": "172.66.147.243",
      "ttl": 300
    }
  ]
};

console.log("Deploy target: " + domain);
console.log("Expected users: " + expectedUsers);
console.log("Primary URL: " + url);
console.log("DNS metadata loaded: " + dnsInfo.status);
