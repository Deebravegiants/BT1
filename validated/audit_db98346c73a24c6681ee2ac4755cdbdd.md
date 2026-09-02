## Title
Webhook shop identity is not authenticated by the HMAC — cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats any request whose raw body's HMAC matches the app's `api_secret_key` as "verified to have come from Shopify" for *any* shop, because the HMAC signature only covers the raw request body — never the `shop-domain` header that is subsequently trusted as the tenant identity passed to the app's webhook handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `#shop` is read directly and unauthenticated from the `x-shopify-shop-domain`/`shopify-shop-domain` header: [1](#0-0) [2](#0-1) 

`Utils::HmacValidator.validate_signature` computes and compares the HMAC solely over `verifiable_query.to_signable_string`, i.e. the body: [3](#0-2) 

`Registry.process` gates on that body-only HMAC check, then forwards the unauthenticated `request.shop` header value straight into the handler as the tenant identity: [4](#0-3) 

The binding the gem should enforce is: `shop_header == shop_that_the_signed_body_was_generated_for`. Instead the code only enforces `hmac(raw_body, api_secret_key) == received_hmac`, which is independent of the `shop` header. Since `api_secret_key` is shared by the app across every merchant/tenant that installs it, any two webhook deliveries produced for two different shops are signed with the *same* key over *different* bodies. An attacker who legitimately installs the target app on their own (attacker-controlled) shop will receive genuinely-signed webhook deliveries (valid body + valid HMAC) for their own shop's events. Nothing then prevents them from re-POSTing that exact same `(raw_body, hmac)` pair directly to the app's public webhook endpoint while substituting the `shop-domain` header for a victim shop's domain. `HmacValidator.validate` still returns `true` (the body and HMAC are unmodified and genuinely valid), so `Registry.process` accepts the request and invokes the handler with `WebhookMetadata.shop` set to the victim's shop while `body` is fully attacker-controlled content, as documented and consumed by host apps: [5](#0-4) 

This directly contradicts the gem's own documentation, which states that `Registry.process` "will verify the request did indeed come from Shopify" for the request as a whole — including the shop attribution used by the handler: [6](#0-5) 

### Impact Explanation
This breaks the tenant/identity binding `shop == authenticated_sender`, exactly the class of flaw called out in scope (a field — `shop` — acted upon by the handler but not covered by the HMAC). It allows an unprivileged internet user (any developer who can install the vulnerable/target app on a shop they control) to forge webhook events attributed to an arbitrary other merchant that uses the same app, with attacker-chosen body content (e.g., spoofed `orders/create`, `customers/update`, `app/uninstalled`, etc.). Any host application that keys business logic (order processing, billing, notifications, data sync, uninstall handling) off `WebhookMetadata#shop` is exposed to cross-tenant data injection/corruption without ever needing the app's `client_secret`, an access token, or a privileged account — only the ability to install the app once as an ordinary merchant. This meets the Critical "cross-tenant access" bar.

### Likelihood Explanation
Likelihood is high for any app that is public/self-serve installable: an attacker can freely create a Shopify development store, install the target app to receive at least one genuinely signed webhook, then replay it against the app's public webhook endpoint with a modified shop header. No secret material, MITM, or privileged access is required — the webhook HTTP endpoint is by design internet-reachable.

### Recommendation
Bind the shop header (and ideally topic/webhook-id) into the value that is HMAC-verified, or otherwise cryptographically tie the verified body to the claimed shop before it is handed to the handler — e.g., include the shop domain in the signable string, or cross-check `request.shop` against a shop known to have that webhook registered/subscribed before dispatching to the handler. At minimum, update `Utils::HmacValidator`/`Webhooks::Request` so that `to_signable_string` incorporates the shop-domain header, and document clearly that `shop` is otherwise attacker-controlled if this is not fixed.

### Proof of Concept
1. Attacker creates their own Shopify store `attacker.myshopify.com` and installs the target app (built on this gem), registering it for topic `orders/create`.
2. Attacker performs an action in their own store that triggers Shopify to deliver a legitimately-signed webhook to the app's registered HTTP endpoint:
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of BODY>`, `x-shopify-topic: orders/create`
   - Body: `BODY` (attacker fully controls the order contents on their own store)
3. Attacker captures this exact `(BODY, valid HMAC)` pair (e.g., via their own reverse proxy/logging in front of the app, which they control since it's their own installation).
4. Attacker sends a new HTTP POST directly to the app's public webhook URL with:
   - `x-shopify-shop-domain: victim.myshopify.com` (any other shop that has this app installed)
   - `x-shopify-hmac-sha256: <the same valid HMAC captured in step 3>`
   - Body: the same `BODY` from step 3
5. `Utils::HmacValidator.validate` succeeds because the body and HMAC are unchanged and were validly produced with the app's `api_secret_key`.
6. `Webhooks::Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's order data>, ...)`, causing the host application to process attacker-controlled data under the victim shop's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
