### Title
Webhook shop-domain header spoofing due to HMAC signature covering only the raw body — cross-tenant webhook processing ([File: lib/shopify_api/webhooks/request.rb])

### Summary
The webhook HMAC verification in this gem only authenticates the raw request body; the `shop-domain` header that the gem hands to the app's webhook handler is never covered by the signature. An attacker who owns a shop that has the app installed (an unprivileged, ordinary merchant with no special credentials) can capture a genuinely Shopify-signed webhook delivered to their own shop and replay the identical body/HMAC pair to the app's shared webhook endpoint while substituting a different `X-Shopify-Shop-Domain` header. `ShopifyAPI::Webhooks::Registry.process` will accept it as valid and dispatch it to the app's handler tagged with the attacker-chosen shop, breaking the equality that should hold: `HMAC-verified sender == shop the event is attributed to`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, completely outside the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the signature strictly against `to_signable_string`: [3](#0-2) 

`Registry.process` performs only this body-only HMAC check, then immediately trusts `request.shop` (the unauthenticated header) when building the data handed to the app's handler: [4](#0-3) 

Because the signature never binds the shop-domain header to the payload, any party that obtains one valid `(body, hmac)` pair — trivially achievable by installing the app on their own store and receiving one real webhook — can re-send that exact pair with an arbitrary `shop-domain` header value. The gem's `process` method will pass HMAC validation and call the registered handler with `shop:` set to the attacker-supplied value, exactly the same as the reported bug class ("a field acted on but not covered by the HMAC").

### Impact Explanation
This is a cross-tenant integrity break: the app's webhook handler receives data it will treat as authoritative for shop X while the equality `verified-signer-shop == handler-shop` never actually held. In typical multi-tenant apps that key business logic/database writes off `data.shop` from `WebhookMetadata`, this allows an unprivileged attacker to inject events (with content of their choosing, since they control their own shop's webhook payloads such as `products/update`, `orders/create`, etc.) that get attributed to and processed under a victim shop's identity — e.g., corrupting another merchant's cached data, triggering unauthorized side effects, or polluting per-shop state, all without needing the app's `client_secret`, an access token, or any credential belonging to the victim. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app that (a) is installed on more than one shop and (b) uses this gem's `Webhooks::Registry.process`/`Webhooks::Request` as documented. The attacker only needs to be a legitimate, unprivileged merchant with the app installed — no special access is required to obtain a real `(body, hmac)` pair for their own shop, and HTTP header replay to a public webhook endpoint requires no authentication.

### Recommendation
Include the shop-domain (and ideally topic/api-version) in the signable content that is HMAC-verified, or otherwise cryptographically bind the header to the verified payload before it is handed to `WebhookMetadata`/handlers — e.g., verify `request.shop` against the shop associated with the specific webhook subscription/session that was expected, not merely trust the header once body HMAC passes.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and lets Shopify deliver a real webhook, e.g. `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H` (computed by Shopify over `B` using the app's real client secret — attacker doesn't need to know the secret, Shopify computes and sends it).
2. Attacker replays the captured request to the same app endpoint, keeping body `B` and header `X-Shopify-Hmac-Sha256: H` unchanged, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body normally; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (== `B`) and finds it matches `H` — validation succeeds.
4. The handler is invoked with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, i.e., the app processes the attacker's event data as though it originated from the victim shop.

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
