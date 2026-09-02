## Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its verifiable signable string from the raw body only, while the `shop` (tenant identifier) is read from a header that is never included in the HMAC-signed material. Since the app's `api_secret_key` is shared across every shop that has installed the app, any merchant that receives a legitimately-signed webhook can replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting a different value in the `x-shopify-shop-domain` / `shopify-shop-domain` header. `HmacValidator` will still report the signature as valid because it only checks the body, letting the attacker's webhook be attributed to an arbitrary victim shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw request body: [1](#0-0) 

`shop` is read independently from a header that plays no part in that signable string: [2](#0-1) 

`HmacValidator.validate` / `validate_signature` compute and compare the HMAC solely against `verifiable_query.to_signable_string` (i.e. the raw body), never touching `shop`: [3](#0-2) 

`Registry.process` accepts the request once `HmacValidator.validate` succeeds, then forwards `request.shop` directly to the handler as the trusted tenant identity, with no additional binding check between `shop` and the signed body: [4](#0-3) 

The identity binding that should hold is: `hmac == HMAC(secret, body || shop)` (or equivalent), so that the shop attribution cannot be altered without invalidating the signature. Instead the actual binding enforced is `hmac == HMAC(secret, body)`, independent of `shop`. Because `api_secret_key` is the same secret for every shop that installs the app (it's the app's client secret, not a per-shop secret), any authenticated merchant that legitimately receives webhooks from Shopify can capture a valid `(body, hmac)` pair from their own shop and resend it to the app's webhook endpoint with the `shop-domain` header rewritten to point at a different (victim) shop. The signature check in `HmacValidator` still passes because it never examines the `shop` header, and `Registry.process` will hand off `WebhookMetadata` claiming to be from the victim shop.

### Impact Explanation
This breaks the tenant-isolation guarantee the HMAC is meant to provide for webhook delivery: `data.shop` reported to the host application's webhook handler is not actually bound to the cryptographically verified payload. A host application that uses `WebhookMetadata#shop` to select which merchant's data to update (a common and encouraged pattern, since `Registry.process` is documented to hand a trusted `shop` to handlers) can be tricked into writing/mutating data under a different tenant's identity — a cross-tenant access/write vulnerability driven entirely from this gem's own webhook verification logic.

### Likelihood Explanation
The only requirement is having installed the app on any real shop (an "unprivileged internet user" from Shopify's perspective, satisfying the rule's threat model) so as to receive at least one genuine webhook delivery whose `(body, hmac)` pair can be captured and replayed with a modified `shop-domain` header. No access to `api_secret_key`, tokens, or the target/victim's credentials is required, matching the reachable, unprivileged threat model called for in this scan.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) value inside the HMAC-signed material in `Webhooks::Request#to_signable_string`, or otherwise cryptographically bind the `shop-domain` header to the verified payload before it is trusted and passed to webhook handlers in `Registry.process`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. body `{"id":1}` with headers:
   - `x-shopify-hmac-sha256: <valid HMAC of body>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
2. Attacker resends the exact same body and HMAC to the app's webhook endpoint, but changes the header to:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `to_signable_string` (the body only) and it matches, so `Registry.process` in `lib/shopify_api/webhooks/registry.rb` accepts the request and calls the handler with `shop: "victim-shop.myshopify.com"`, even though the payload never originated from Shopify for that shop.

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
