### Title
Webhook shop attribution is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/utils/hmac_validator.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
The gem's webhook authenticity check verifies only the HMAC over the raw request body, while the `shop` value used to attribute the webhook to a specific tenant is read from an HTTP header that is completely outside the signed material. Any actor who can obtain one legitimate `(body, hmac)` pair — for example from their own Shopify dev/partner store with the app installed — can replay that exact body and signature to the app's public webhook endpoint while substituting an arbitrary `shop-domain` header, causing the payload to be processed as if it belonged to a different (victim) shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop` accessor, which is used to attribute processed data to a tenant, is pulled from the `shopify-shop-domain` / `x-shopify-shop-domain` header and is never part of the signable string: [2](#0-1) 

`HmacValidator.validate` computes the HMAC strictly over `verifiable_query.to_signable_string` (i.e., the body only) and compares it with `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` performs exactly that HMAC check and then immediately hands `request.shop` — the unauthenticated header value — to the registered handler as the authoritative tenant identity, with no further validation that this shop matches whatever tenant actually produced the signed body: [4](#0-3) 

The identity binding the code should enforce is:
`shop-used-for-signature-validation == shop-used-for-tenant-attribution`

but the actual enforced equality is only:
`HMAC(body) == received_hmac`,

with `shop` supplied independently and unauthenticated. This is a direct instance of "a field acted on but not covered by the HMAC."

### Impact Explanation
Because `shop` is not covered by the signature, an attacker who has access to one legitimate `(raw_body, hmac)` pair (trivially obtainable by installing the app on their own Shopify store — a normal, unprivileged action available to anyone) can POST that same body/HMAC to the app's public webhook URL while setting the `X-Shopify-Shop-Domain` header to a victim shop's domain. The `Webhooks::Registry.process` validates the HMAC successfully (it only checks the body) and dispatches the payload to the handler tagged with the victim's shop via `WebhookMetadata#shop`. If the host application keys any state changes, data storage, uninstall handling, or business logic on this `shop` value (which is the intended and documented usage of `WebhookMetadata`), the attacker can inject or corrupt data attributed to a tenant they do not control — a cross-tenant confusion/access issue.

### Likelihood Explanation
Exploitation requires no credentials, access tokens, or the app's `client_secret`/`api_secret_key` — only the ability to send an HTTP POST to the app's public webhook endpoint and one previously obtained legitimate webhook body+HMAC pair, which any developer can generate by installing the app on their own store. This satisfies an "unprivileged internet user" threat model.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) as part of the HMAC-signed material, or, failing that, have `Webhooks::Registry.process` cross-check `request.shop` against a value that is itself cryptographically bound to the request (e.g., verify the shop against the session store keyed by a value derived from a signed component), rejecting the webhook if the header-derived shop cannot be corroborated. At minimum, document that host applications must independently verify that `request.shop` corresponds to a shop that has genuinely installed the app before trusting it, and treat it as untrusted otherwise.

### Proof of Concept
1. As a developer, install the target app on your own Shopify dev store `attacker-shop.myshopify.com` and capture one legitimate webhook delivery, e.g. `orders/create`, saving the raw body `B` and the `X-Shopify-Hmac-Sha256` header value `H` (both valid because `H = HMAC-SHA256(api_secret_key, B)`).
2. Send a new POST request directly to the app's public webhook endpoint with:
   - Body: the exact captured `B`
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid for `B`)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (attacker-controlled, arbitrary)
   - Header `X-Shopify-Topic`: same topic as captured
3. `ShopifyAPI::Webhooks::Registry.process` computes `Utils::HmacValidator.validate(request)` using only `B`, which succeeds since `H` matches `B`. [4](#0-3) 
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`, and any application logic keyed on `shop` (e.g., updating victim's order records, triggering victim-side side effects) executes against the wrong tenant, despite the payload never having originated from or being signed on behalf of that tenant.

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
