### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `ShopifyAPI::Webhooks::Registry.process` trusts the unauthenticated `shop-domain` (and `topic`/`webhook-id`) headers to build the `WebhookMetadata` passed to the host application's handler. This breaks the identity binding `HMAC-verified bytes == data acted upon`.

### Finding Description
`Utils::HmacValidator.validate` verifies a webhook request by recomputing an HMAC over `verifiable_query.to_signable_string` and comparing it to the `hmac-sha256`/`x-shopify-hmac-sha256` header value: [1](#0-0) 

For webhooks, `to_signable_string` is defined as only the raw HTTP body: [2](#0-1) 

Meanwhile, `shop`, `topic`, and `webhook_id` are pulled straight from HTTP headers, which are never included in the signed payload: [3](#0-2) 

`Registry.process` validates only the HMAC (i.e., only the body) and then constructs `WebhookMetadata` directly from the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id`, handing it to the host app's handler as trusted tenant context: [4](#0-3) [5](#0-4) 

Because the app's `client_secret` (the HMAC key) is the same across every shop that has the app installed, a merchant who installs the app on their own store legitimately receives real webhook deliveries with a body and a valid HMAC computed with that shared secret. Since the `shop-domain`, `topic`, and `webhook-id` headers are not part of the signed bytes, that same merchant can replay the captured `(body, hmac)` pair to the app's webhook endpoint while substituting a different `x-shopify-shop-domain` (and/or topic/webhook-id) header value. `Utils::HmacValidator.validate` will still pass (it only checks the body), and `Registry.process` will hand the host app a `WebhookMetadata` claiming the forged shop/topic, even though Shopify never sent that webhook for that shop. This is exactly the "field acted on but not covered by the HMAC" class of bug from the reference report's precision-loss issue: the identity-binding equality `verified_bytes == data_the_app_trusts` does not hold, because `verified_bytes = body` while `data_the_app_trusts = {shop, topic, webhook_id} ⊄ body`.

### Impact Explanation
This allows cross-tenant webhook spoofing/confusion: an attacker who controls one installation of the app (their own shop) can forge webhook deliveries that appear, to the host application, to originate from a different, victim shop. Any host-app logic that keys off `WebhookMetadata#shop` (e.g., updating that shop's local records, triggering per-shop side effects, or looking up a session/store by `shop`) can be poisoned with attacker-controlled data attributed to a shop the attacker does not own. This matches the "Critical - cross-tenant access" impact bucket, since it lets one tenant inject data/events into another tenant's processing pipeline via a mechanism the gem exposes as "verified."

### Likelihood Explanation
Any developer who installs the app for their own store (an ordinary, unprivileged action requiring no special access, secrets, or leaked credentials) can capture one real webhook `(body, hmac)` pair from their own shop and immediately replay it with a modified `shop-domain` header — no cryptographic secret is needed because the header being forged is outside the signed content. This is directly reachable through the gem's own public `Registry.process` / `Webhooks::Request` API with only a single legitimate app installation.

### Recommendation
Bind the tenant-identifying fields to the HMAC verification, not just the body. Either:
- Include the `shop-domain` (and ideally `topic`, `webhook-id`) header values in the signed/verified string used by `Webhooks::Request#to_signable_string`, or
- Have `Registry.process` independently authenticate/authorize the `shop` value (e.g., by resolving and validating it against a known, previously registered session for that shop) before constructing `WebhookMetadata`, rather than trusting the raw header.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` (a normal, unprivileged installation).
2. Shopify sends a real webhook to the app's endpoint with body `B`, and header `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures this request and re-sends it to the same endpoint, keeping body `B` and the same `hmac-sha256` header, but changing `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only — it still matches, so validation passes: [6](#0-5) 
5. `Registry.process` then builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the forged `shop-domain` header value and dispatches it to the app's handler as if Shopify itself had sent this webhook for `victim-shop.myshopify.com`: [7](#0-6)

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
