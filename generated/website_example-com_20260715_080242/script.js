const expectedUsers = 2500;
const domain = "example.com";
const url = "https://example.com";
const dnsInfo = {
  "status": 0,
  "records": [
    {
      "type": 1,
      "data": "172.66.147.243",
      "ttl": 42
    },
    {
      "type": 1,
      "data": "104.20.23.154",
      "ttl": 42
    }
  ]
};
const publicIp = {
  "ip": "88.236.103.56"
};

console.log("Deploy target: " + domain);
console.log("Expected users: " + expectedUsers);
console.log("Primary URL: " + url);
console.log("DNS metadata loaded: " + dnsInfo.status);
console.log("Public IP: " + publicIp.ip);
