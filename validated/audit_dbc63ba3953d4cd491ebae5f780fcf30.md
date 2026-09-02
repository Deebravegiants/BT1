### Title
Webhook shop identity is not bound to the HMAC, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb], [File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body. The `shop` value that is extracted from the `X-Shopify-Shop-Domain` header and handed to the application's webhook handler is never covered by that HMAC, so the tenant identity used downstream is not the identity that was actually authenticated.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery` and defines the signable string as the raw body only: [1](#0-0) 

The `shop` accessor is read straight from the unauthenticated header: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately hands `request.shop` to the app's handler as the tenant identity, with no cross-check that this shop matches anything cryptographically tied to the signature: [3](#0-2) 

`HmacValidator.validate` itself only ever checks `verifiable_query.to_signable_string` (the body) against `verifiable_query.hmac`; it has no notion of `shop` at all: [4](#0-3) 

The broken identity binding, stated as an equality that the code fails to enforce:
`shop used by WebhookMetadata/handler (request.shop, from header)` **should equal** `shop cryptographically bound by the verified signature (HMAC(body, api_secret_key))` — but the HMAC only signs the body, never the shop header, so any shop value can be paired with any validly-signed body.

### Impact Explanation
Because the app's `api_secret_key` is shared across every shop that has the app installed, any merchant who installs the app on their own store can legitimately receive a webhook with a valid `(body, hmac)` pair (e.g., from `orders/create` on their own store). They can then submit that exact body and HMAC directly to the app's public webhook endpoint while substituting `X-Shopify-Shop-Domain` with a victim shop's domain. `Registry.process` will accept it as authentic because the HMAC check passes, and the attacker-supplied body is dispatched to the application's handler tagged with the victim's `shop`. If the host app's handler (following this gem's documented `WebhookMetadata` pattern) looks up the victim's session/store by `shop` and applies the forged payload, this results in cross-tenant data injection/corruption — impersonating Shopify's webhook delivery for a shop the attacker does not control, without needing the app's `client_secret`, an access token, or any privileged credential.

### Likelihood Explanation
The attacker only needs a normal, unprivileged app installation on any store they control (trivial to obtain for a public app) plus the ability to POST to the app's public webhook URL, which is inherent to how webhook endpoints are exposed. No secret material, TLS interception, or social engineering is required, making this readily reachable by an unprivileged internet user.

### Recommendation
Bind the shop identity into the value that is authenticated, e.g. include the `shop` (and/or `topic`, `webhook_id`) in `to_signable_string`, or require the caller to supply the expected shop for the webhook and compare it against a shop bound to the session/install record before invoking the handler, rather than trusting the header value implicitly once the body HMAC passes.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and captures a legitimate webhook delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (H = HMAC-SHA256(api_secret_key, B)), along with `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker crafts a new POST to the app's public webhook endpoint reusing body `B` and header `H` unchanged, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `H` against `HMAC(api_secret_key, B)` — this still matches, so validation passes.
4. The handler is invoked via `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` with `shop == "victim.myshopify.com"`, even though nothing about `B`/`H` was ever produced for that shop. [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
