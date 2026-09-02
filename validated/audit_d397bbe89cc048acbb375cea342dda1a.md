### Title
Webhook shop identity spoofing — the `shop` field trusted by webhook handlers is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` reads the shop domain from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, but the HMAC signature validated by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body. Since the app's `api_secret_key` is the *same* for every shop installation of the app (it is not per-shop), any actor who can obtain one genuine `(raw_body, hmac)` pair — e.g., by installing the app on their own shop and observing/replaying a webhook event they legitimately receive — can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary victim shop domain in the unsigned `x-shopify-shop-domain` header. The gem will report the request as HMAC-valid and hand the attacker-chosen shop to the application's webhook handler.

### Finding Description
The equality that should hold is:

`shop value trusted by the handler == shop value cryptographically bound by the HMAC`

In practice:
- `Webhooks::Request#hmac` and `#to_signable_string` only bind the raw body: [1](#0-0)  and [2](#0-1) .
- `Webhooks::Request#shop` is read straight from the unauthenticated header with no relation to the signature: [3](#0-2) .
- `HmacValidator.validate` verifies the signature purely against `to_signable_string` (the body), never the shop: [4](#0-3) .
- `Registry.process` validates the HMAC and then immediately trusts `request.shop` to build the data handed to the app's business logic: [5](#0-4) .

Because the HMAC secret (`api_secret_key`/`client_secret`) is shared across all shops that install the same app, a valid `(body, hmac)` pair generated for one shop's webhook remains cryptographically valid no matter which `shop-domain` header accompanies it. The HMAC therefore proves only "this app's secret produced this body's signature" — it proves nothing about which shop the event pertains to.

### Impact Explanation
This breaks the tenant boundary the webhook system is supposed to guarantee: an unprivileged actor who merely installs the app on a shop they control can, after harvesting one legitimate `(body, hmac)` pair from their own shop's traffic, forge webhook deliveries that the gem will validate as authentic while attributing the payload to any victim `shop` domain of their choosing. Any host application logic that uses `WebhookMetadata#shop` to look up per-tenant sessions, gate access, or perform per-shop side effects (the documented and expected usage pattern of `Registry.process`) can be tricked into acting on/for a shop the attacker does not control — i.e., cross-tenant access driven purely by an unsigned header. This matches the Critical impact category of cross-tenant access.

### Likelihood Explanation
Likelihood is limited by the practical need to first obtain a genuine `(raw_body, hmac)` pair, but this is trivially achievable without any special privilege: installing the app on a shop is available to any internet user, and normal app usage naturally generates a stream of webhook deliveries (e.g., `app/uninstalled`, `shop/update`) whose bodies are often static or predictable per topic. Because the app secret is shop-independent, the harvested pair is directly reusable against any other tenant.

### Recommendation
Bind the shop identity into the value that is actually verified: include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in the signable string used by `HmacValidator`, or otherwise require verification that the shop asserted in the header matches a shop-scoped secret/session, rather than validating a shop-agnostic body signature and separately trusting an unauthenticated header for that identity.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (no special privilege required).
2. Attacker observes/logs a legitimate webhook POST received by the app's endpoint, capturing `raw_body` and the `x-shopify-hmac-sha256` header (valid under the app's shared `api_secret_key`).
3. Attacker resends the exact same `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` succeeds (it only checks the body against the secret) — see [6](#0-5) .
5. `Registry.process` calls the handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` — see [7](#0-6)  — even though the event has nothing to do with the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
