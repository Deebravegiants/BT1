### Title
Webhook `shop` (and `topic`/`webhook-id`) identity is trusted from unauthenticated headers while the HMAC only covers the raw body — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw request body, but the tenant-identifying `shop-domain` header (and `topic`/`webhook-id`) is never included in the HMAC-signed material. `Registry.process` accepts any request whose body/HMAC pair is valid and then forwards the *header-derived* `shop` value to the app's webhook handler as authoritative tenant identity, even though that header was never bound to the signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `to_signable_string`, i.e. purely from the body: [3](#0-2) 

`Registry.process` gates on that body-only HMAC check, then immediately trusts `request.shop`/`request.topic` (both parsed straight from attacker-controllable HTTP headers) as the tenant/topic identity handed to the app's handler: [4](#0-3) 

The identity binding that should hold is:
`shop authenticated by HMAC == shop delivered to the handler`

but the actual binding enforced by the code is only:
`bytes(raw_body) authenticated by HMAC == bytes(raw_body) parsed`,
with `shop` (and `topic`, `webhook_id`) sitting entirely outside the signed envelope. Any two requests that share the same body will produce the same valid HMAC regardless of what `shop-domain` header accompanies them.

### Impact Explanation
An unprivileged internet user who can obtain one legitimately-signed `(raw_body, hmac)` pair — trivially done by installing the app on their own free/test store and receiving a genuine webhook Shopify sends them — can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header for a victim shop. Because `HmacValidator.validate` never inspects the header, the forged request passes validation, and `Registry.process` builds `WebhookMetadata` attributing the event to the victim shop: [5](#0-4) 

Any application logic keyed off `WebhookMetadata#shop` (order/product ingestion, App uninstall handling, GDPR/compliance webhooks, billing state, etc.) can be triggered cross-tenant purely by header forgery, without ever knowing `api_secret_key` — this is a cross-tenant access vector rooted entirely in this gem's own verification logic.

### Likelihood Explanation
High. No secret material is required; an attacker only needs one genuine webhook body+signature pair from their own (attacker-controlled) shop and the ability to send an arbitrary HTTP request with custom headers to the app's public webhook endpoint — both trivially available to any internet user who installs the target app on a store they control.

### Recommendation
Bind the `shop-domain` (and ideally `topic`/`webhook-id`) into the signed material, or otherwise cryptographically tie the header values to the verified payload before trusting them — e.g., include the shop domain in the value passed to `to_signable_string`, or independently authenticate the shop identity (such as validating it against a shop known to have a stored, previously-obtained access token) rather than accepting it verbatim from an unauthenticated header in `Registry.process`.

### Proof of Concept
1. Attacker installs the vulnerable app on `attacker-shop.myshopify.com` and triggers any webhook (e.g. `orders/create`) to receive a genuine `(raw_body, x-shopify-hmac-sha256)` pair from Shopify.
2. Attacker sends a POST to the app's webhook endpoint with:
   - the same `raw_body` and `x-shopify-hmac-sha256` value captured in step 1,
   - `x-shopify-shop-domain: victim-shop.myshopify.com`,
   - `x-shopify-topic` set to any topic value.
3. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) verifies successfully because it only checks `raw_body` against the secret.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)`, causing the app to process attacker-supplied data as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
