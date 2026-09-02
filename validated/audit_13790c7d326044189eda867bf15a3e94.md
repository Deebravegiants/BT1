### Title
Webhook shop identity not bound to HMAC signature enables cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity by checking an HMAC over the raw request body only, but the `shop` value it hands to the host application's handler is read from an HTTP header that is completely outside that HMAC's coverage. This breaks the intended binding "shop the HMAC vouches for" == "shop the app acts on," analogous to the report's core bug class of an operative field (there, the ETH/USD price ratio; here, the tenant identity) not being covered by the mechanism (there, the oracle price feed; here, the HMAC signature) that is supposed to guarantee its integrity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is derived independently from the `X-Shopify-Shop-Domain` header, never entering the signable string: [2](#0-1) 

`Registry.process` validates the HMAC (over body bytes only) and then forwards `request.shop`, taken straight from the unauthenticated header, into `WebhookMetadata` given to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes/compares the signature purely against `to_signable_string`, i.e., the body — it never incorporates `shop`, `topic`, or any other header: [4](#0-3) 

The equality that should hold is:
`shop authenticated by HMAC == shop delivered to WebhookMetadata.shop`

But because `to_signable_string` only covers `@raw_body`, and `shop` comes from a header, the actual guarantee reduces to:
`bytes verified by HMAC (request body) != shop acted upon (header value)`

Any entity capable of obtaining one genuinely Shopify-signed webhook for their own shop (i.e., a normal merchant with a legitimately installed app — no leaked secrets, access tokens, or privileged access required) can capture that valid `(raw_body, hmac)` pair and re-send it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header value replaced by a victim shop's domain. `HmacValidator.validate` still returns true because the body bytes and HMAC are unmodified, and `Registry.process` will dispatch the handler with `WebhookMetadata.shop` set to the attacker-chosen victim shop.

### Impact Explanation
If a host application uses `WebhookMetadata.shop` to select which merchant's data to update, delete, or process (e.g., `customers/redact`, `orders/paid`, `app/uninstalled`), this cross-tenant identity confusion lets an attacker who controls their own shop's legitimate webhook deliveries cause the app to attribute payload data to, or act on behalf of, a different tenant. This meets the High-severity bar of cross-tenant/scope-check bypass: the app's identity boundary (shop tenant) is not actually enforced by the cryptographic control it relies on.

### Likelihood Explanation
The prerequisite is only that the attacker is a legitimate merchant/user of the app (an "unprivileged internet user" relative to other tenants), able to receive at least one real webhook for their own shop and replay it with a modified header to the app's public webhook receiver endpoint. No access token, `client_secret`, or privileged access is required — this is entirely within reach of any app installer.

### Recommendation
Include `shop` (and `topic`, `webhook_id`, `api_version`) in the HMAC-signed material used for verification, or otherwise cryptographically bind the header-derived `shop` to the verified payload before it is trusted by `Registry.process`/`WebhookHandler#handle`. At minimum, document and enforce that host applications must independently authenticate the shop domain against the payload contents (e.g., verify it matches an owned/known shop from session storage) rather than trusting the header value that `Registry.process` currently forwards unchecked.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` and receives a legitimate webhook: body `B`, header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, header `X-Shopify-Hmac-Sha256: H` (valid for body `B`).
2. Attacker replays the exact same request to the app's webhook endpoint, but rewrites `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`, leaving `B` and `H` untouched.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= B`) and compares to `H` — validation succeeds because `B`/`H` are unchanged: [5](#0-4) 
4. `handler.handle` is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, even though Shopify never issued a webhook about `victim-shop`: [6](#0-5)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
