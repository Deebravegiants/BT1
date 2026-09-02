### Title
Webhook `shop` field is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` binds a webhook's `topic`, `shop`, `api_version`, and `webhook_id` to whatever values are supplied in the raw HTTP headers, but the HMAC signature that `Utils::HmacValidator` verifies covers only the raw request body. Because the `shop` identity is not part of the signed bytes, an attacker who possesses one valid, HMAC-signed webhook body (trivially obtainable for any shop that installs the app, since the same app `client_secret` signs webhooks for every tenant) can replay that body to the app's webhook endpoint while substituting an arbitrary `shop-domain` header. `Registry.process` will treat the payload as authentic for the victim shop, breaking the binding "shop that produced/authenticated the signed bytes == shop attributed to the data."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read straight from unauthenticated headers and are not part of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` only checks that `hmac` matches the signature computed over `to_signable_string` (i.e., the raw body) with the app's `api_secret_key`: [3](#0-2) 

`Registry.process` accepts the request once that body-only HMAC check passes, then dispatches the handler using the unauthenticated `request.shop` (and `request.topic`) values, without any additional check that the body actually originated from that shop: [4](#0-3) 

The equality the code should enforce but does not is: `shop that authenticated/produced the signed bytes == shop the handler is told the data belongs to`. Since Shopify signs webhooks per-app (not per-shop) with the app's single `client_secret`, any merchant who installs the app can capture one legitimately signed `(raw_body, hmac)` pair from their own shop's webhook delivery, then POST it to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header naming a different, victim shop. `HmacValidator.validate` still succeeds because the body/hmac pair truly matches, and `Registry.process` calls the handler with `shop: request.shop` set to the attacker-chosen victim domain and `body: request.parsed_body` containing the attacker's own (or manipulated) payload content.

### Impact Explanation
Any application built on this gem that uses `WebhookMetadata#shop` from `Registry.process` to key per-tenant state (e.g., "look up shop X's record and apply this order/customer/product update") can be tricked into writing/mutating another merchant's data using attacker-controlled body content, since the shop attribution is unauthenticated. This is a cross-tenant data-confusion vector reachable by any unprivileged user who can install the app on at least one shop (a normal, unprivileged action for a public app) — no access token, `client_secret`, or privileged account is required from the attacker beyond normal app installation.

### Likelihood Explanation
High likelihood: the only prerequisite is installing the target app on an attacker-controlled shop (the normal onboarding flow for any public Shopify app) and triggering one webhook delivery to capture a valid `(raw_body, hmac)` pair. No secrets, tokens, or special privileges are needed to then replay that pair against the same endpoint with a forged shop header.

### Recommendation
Include the shop identity (and other trust-critical fields like `topic`, `webhook_id`, `api_version`) inside the HMAC-signed material used for verification, or otherwise cryptographically bind the `shop-domain` header to the signed body before `Registry.process` uses it to route/attribute data. At minimum, document that host applications must not trust `request.shop` for authorization/tenant-selection purposes without independently correlating it (e.g., cross-checking against a stored, previously-authenticated session for that shop) — and preferably make `HmacValidator`/`Request` sign over `shop + topic + raw_body` rather than `raw_body` alone.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, completing normal OAuth (no special privilege needed).
2. Attacker triggers any webhook subscribed by the app (e.g., `orders/create`) on their own shop, capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent — both are valid because they are signed with the app's single `client_secret`.
3. Attacker replays the exact same body/hmac pair to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` builds a request object exposing `shop == "victim.myshopify.com"` from the header (`lib/shopify_api/webhooks/request.rb:20-23`).
5. `HmacValidator.validate(request)` succeeds because the signature check only covers `raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:12-31`).
6. `Registry.process` invokes the app's handler with `shop: "victim.myshopify.com"` and the attacker's own webhook body, causing the host app to attribute attacker-controlled data to the victim tenant. [4](#0-3)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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
