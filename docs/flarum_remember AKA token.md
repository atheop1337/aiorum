# 🔑 Authentication Token in Flarum

Flarum uses the **`flarum_remember`** cookie as an authentication token.  
According to the [official documentation](https://docs.flarum.org/rest-api/), this token expires only after **5 years of inactivity**.

---

## 📥 How to obtain `flarum_remember`

To get the `flarum_remember` cookie:

1. Perform any authorized request (e.g., creating a post, sending a PATCH request, or another action that requires login).  
2. Open your browser’s **network analyzer** (developer tools → network tab).  
3. Copy the **`flarum_remember`** cookie from the request headers.  

This cookie is your persistent authentication token.

---

⚠️ **Note:** Handle this token carefully — leaking it is equivalent to leaking your account access.
