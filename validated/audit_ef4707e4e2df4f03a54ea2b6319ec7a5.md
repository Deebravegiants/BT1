Based on the investigation, I found a concrete analog: the webhook HMAC in this gem signs only the raw request body and never binds it to the `shop` (tenant) identity carried in the `x-shopify-shop-domain` header.

### Title
Webhook HMAC does not bind the shop-domain header, allowing cross-tenant webhook replay/spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `ShopifyAPI::Utils::HmacValidator.validate` checks in `ShopifyAPI::Webhooks::Registry.process` covers the body bytes but not the `shop` value the app trusts for tenant attribution.

### Finding Description
`Request#to_signable_string` is defined as `@raw_body` only [1](#0-0) , while `Request#shop` is read verbatim from the `x-shopify-shop-domain`/`shopify-shop-domain` header with no cryptographic tie to the signature [2](#0-1) . `Registry.process` validates only `Utils::HmacValidator.validate(request)` (i.e., HMAC over the body) before dispatching the handler with `request.shop` used as the tenant identity [3](#0-2) . `HmacValidator.validate_signature` computes the HMAC purely from `to_signable_string` (the body) [4](#0-3) .

The identity binding broken: `shop-domain header verified == shop-domain header used for tenant dispatch` does not hold, because the signature only certifies `raw_body verified == raw_body parsed`, and the shop header is outside that scope. Since all shops installed on a given app share the same `api_secret_key`, any party who can capture one genuine, HMAC-signed webhook body for their own shop (e.g., by installing the app themselves, an unprivileged action) can resend that exact body to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` value. The HMAC still validates because it never covered the header, and `Registry.process` will hand the handler `WebhookMetadata` stamped with the attacker-chosen `shop` alongside the replayed body [5](#0-4) .

### Impact Explanation
This crosses a tenant boundary: an app that trusts `WebhookMetadata#shop` to select/scope per-shop records will process attacker-supplied body content under an arbitrary victim shop's identity while the signature check passes, giving cross-tenant data injection/corruption without ever needing the victim's or the app's credentials.

### Likelihood Explanation
The only capability required is the ability to install the app on any shop (or otherwise obtain one legitimately-signed webhook payload) plus the ability to send arbitrary HTTP requests to the app's public webhook endpoint — both available to an unprivileged internet user/merchant. No `api_secret_key`, access token, or privileged account is needed.

### Recommendation
Include the `shop` (and ideally `topic`) header values in the signable string / HMAC computation, or otherwise cryptographically bind the shop-domain header to the verified payload before it is used as the tenant key in `WebhookMetadata`.

### Proof of Concept
1. Install the vulnerable app on `attacker-shop.myshopify.com`; trigger any webhook (e.g., `orders/create`) and capture the raw request: body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Send a new HTTP request to the same app webhook endpoint with body `B` unchanged, header `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(client_secret, B)` and finds it equals `H`, so validation succeeds [6](#0-5) .
4. `Registry.process` invokes the handler with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: B, ...)`, causing the app to process attacker body content as if it originated from the victim shop [5](#0-4) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
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
