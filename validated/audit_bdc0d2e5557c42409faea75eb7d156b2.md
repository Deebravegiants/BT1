### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from an HTTP header that is **not included** in the data signed by the HMAC. `HmacValidator.validate` only proves that the raw request body was signed with the app's `client_secret` — it says nothing about which shop the body belongs to. An attacker who can obtain one valid `(raw_body, hmac)` pair (trivially available by triggering a webhook on their own store) can replay that exact body/HMAC pair against the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header, and the app will process the payload as if it originated from the victim shop.

### Finding Description
The webhook verification flow is:
1. `Webhooks::Registry#process` calls `Utils::HmacValidator.validate(request)` and, if it returns `true`, immediately builds `WebhookMetadata` using `request.shop`, which is then handed to the app-defined handler: [1](#0-0) 

2. `Request#shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, with no cryptographic binding to the request: [2](#0-1) 

3. Crucially, `Request#to_signable_string` — the data that actually gets HMAC-verified — is only the raw body, and never includes the shop header: [3](#0-2) 

4. `HmacValidator.validate_signature` computes/compares the HMAC purely over `to_signable_string` (i.e. the body) using the app's shared secret, with no notion of "who" sent it: [4](#0-3) 

This breaks the intended identity binding:

`shop authenticated by HMAC` == `shop used to attribute/process the webhook`

Before the attack: for a legitimate Shopify-delivered webhook, `hmac(body)` is valid and the accompanying `shop-domain` header correctly matches the shop that generated `body`.

After the attacker's request: the attacker sends a POST to the app's public webhook endpoint with a `raw_body` + `hmac` pair that Shopify genuinely computed for the **attacker's own shop** (obtainable by triggering any webhook-eligible action on their own store), but with the `shopify-shop-domain` header rewritten to the **victim's** shop domain. `HmacValidator.validate` still returns `true` because it never looks at the shop header — only at `raw_body`. `Registry#process` then invokes the app's handler with `WebhookMetadata.new(shop: request.shop, body: request.parsed_body, ...)`, where `shop` is the attacker-supplied victim domain but `body` is the attacker's own data.

Because webhook endpoints must be publicly reachable (Shopify calls them over the internet with no other authentication mechanism than the HMAC signature), any unprivileged internet user can send this crafted request directly to the endpoint.

### Impact Explanation
This is a cross-tenant confusion vulnerability: an app relying on `WebhookMetadata#shop` to key persistence/authorization decisions (a very common pattern, e.g. "look up shop record by `shop`, then write the webhook body into that shop's data") can be made to write attacker-controlled data into another tenant's records, or trigger tenant-scoped side effects (e.g. app-uninstalled handling, billing state changes) under a victim shop's identity — a cross-tenant access impact.

### Likelihood Explanation
Any internet user who operates (or creates a trial of) a Shopify store can trigger a webhook delivery to the target app (if that store has the app installed) and capture the resulting `(raw_body, hmac)` pair, then replay it directly to the target app's public webhook URL with a forged `shop-domain` header pointing at any other shop. No access token, `api_secret_key`, or privileged account is required — only the ability to observe one's own legitimately delivered webhook and to send an arbitrary HTTP POST.

### Recommendation
Bind the tenant identity into the verified signable content, or otherwise cryptographically tie the `shop-domain` header to the payload before trusting it — e.g. include `shop`, `topic`, and `webhook_id` in `to_signable_string` (matching how `Auth::Oauth::AuthQuery#to_signable_string` binds `shop` into its own signed string), or perform an out-of-band verification that the shop asserted in the header is registered/expected before invoking handlers.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`.
2. Attacker performs an action that triggers a registered webhook topic (e.g. `products/update`), and captures the raw request body `B` and its `X-Shopify-Hmac-Sha256` header value `H` sent by Shopify to the app's webhook endpoint.
3. Attacker sends a new POST directly to the app's public webhook URL with:
   - Body: `B` (unchanged)
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
   - Header `X-Shopify-Topic`: unchanged (or attacker's own, since `topic` also isn't signed)
4. `Utils::HmacValidator.validate(request)` returns `true` because `to_signable_string` only checks `B`, which was genuinely signed by Shopify with the app's `client_secret`.
5. `Registry#process` invokes the app's handler with `shop: "victim-shop.myshopify.com"` and `body` from the attacker's own store, achieving cross-tenant data injection/confusion. [1](#0-0) [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

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
