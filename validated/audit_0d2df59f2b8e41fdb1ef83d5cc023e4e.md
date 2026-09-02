### Title
Webhook `shop` header is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw body only, while the `shop` domain used to attribute the webhook to a tenant is read from an unsigned header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then trusts that same unauthenticated `shop` value when building `WebhookMetadata`, so a party that legitimately receives one valid, HMAC-signed webhook for their own store can replay it to the app's webhook endpoint while swapping the `shop` header to any other shop using the app, causing the app to process attacker-controlled webhook data under a different tenant's identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop` is read from a separate, unsigned header: [2](#0-1) 

`HmacValidator.validate` / `validate_signature` compute and compare the HMAC strictly against `verifiable_query.to_signable_string`, i.e. the body: [3](#0-2) 

`Registry.process` validates that body-only HMAC and then immediately forwards the unauthenticated `request.shop` into `WebhookMetadata`, which is handed to the app's handler as the trusted tenant identifier: [4](#0-3) 

The identity binding that should hold is: `shop authenticated by HMAC == shop used to key/attribute the webhook data`. Here the HMAC only authenticates the body bytes; the `shop` field that the rest of the code (and the app's handler, per the documented `data.shop`/`data.body` contract) treats as verified is never covered by the signature. The gem's own documentation asserts the opposite guarantee, stating that calling `Registry.process` "will verify the request did indeed come from Shopify": [5](#0-4) 

but only the body is verified — the shop attribution is not.

### Impact Explanation
Any shop that has installed the app receives genuinely HMAC-signed webhooks from Shopify for its own store (the HMAC uses the app's shared `client_secret`, not a per-shop secret). Because the `shop` header lives outside the signed payload, that same shop owner can capture one of their own legitimate `(body, hmac)` pairs and replay it against the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a different, victim shop that also uses the app. `HmacValidator.validate` still succeeds (it only checks the body), so `Registry.process` invokes the handler with `WebhookMetadata` claiming the victim shop, injecting attacker-chosen body content under the victim's tenant identity — a cross-tenant data/identity confusion inside the gem's own webhook processing path, which per the rubric maps to Critical (cross-tenant access).

### Likelihood Explanation
Any merchant that installs the app can obtain a validly signed webhook for their own shop through ordinary use (no secret leakage or privileged access required), and headers are trivially attacker-controlled when constructing the replayed HTTP request to the app's public webhook route. The only prerequisite is that the target app processes webhooks for multiple shops via this gem's `Registry.process`/`Request`, which is the documented, standard usage pattern.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signed material verified against the HMAC, or otherwise cryptographically bind `request.shop` to the signature (e.g., verify shop against a per-installation secret/session rather than trusting the header), so that `HmacValidator.validate` can only succeed for the exact `(shop, body)` pair Shopify actually sent.

### Proof of Concept
1. App has two merchants installed: `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, both registered for `orders/create` webhooks with the same handler.
2. Shopify sends a legitimate webhook to the app for `attacker-shop.myshopify.com`:
   ```
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid hmac over body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   Body: {"id": 1, "note": "malicious payload"}
   ```
3. Attacker resends the identical body and HMAC header to the app's webhook route, only changing:
   ```
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   ```
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses this; `Utils::HmacValidator.validate(request)` succeeds because `to_signable_string` only compares the (unchanged) body bytes.
5. `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: {"id"=>1,"note"=>"malicious payload"}, ...)`, causing the app to attribute attacker-controlled data to `victim-shop.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
