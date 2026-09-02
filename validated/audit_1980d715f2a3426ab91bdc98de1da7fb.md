### Title
Webhook `shop-domain` (and `topic`, `webhook-id`, `api-version`) header is trusted by the handler without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates the incoming webhook using `Utils::HmacValidator.validate`, but the HMAC only covers the raw request body, not the `shop-domain`, `topic`, `webhook-id`, or `api-version` HTTP headers. The `WebhookMetadata` struct handed to the app's `WebhookHandler#handle` is built directly from these unauthenticated headers, so the identity of the shop is not bound to the cryptographically verified bytes.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` / `validate_signature` compute and compare the HMAC exclusively against `verifiable_query.to_signable_string`, i.e. the raw body: [2](#0-1) 

`Registry.process` only checks that this body-only HMAC is valid, then immediately reads `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` straight from HTTP headers and forwards them, unauthenticated, into `WebhookMetadata`, which is passed to the app's registered handler: [3](#0-2) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all pulled from the `shopify_header` map with no cryptographic tie to the signed body: [4](#0-3) 

The binding that is broken: `hmac_covers(bytes) == bytes_the_handler_trusts_as_the_shop_identity` is false — the gem verifies `HMAC(body)` but hands the handler `shop = header["shop-domain"]`, which is not part of `body` and is therefore attacker-controllable bytes that were never authenticated by the shared secret. Any party who can produce one request with a *valid* body+HMAC pair for topic/body combination they control (e.g., a legitimate webhook payload from their own low-value/dev shop, or any payload whose HMAC they can compute if they ever get access to the secret for one tenant) can replay it with an arbitrary `shop-domain` header pointing at a different, victim tenant, and the gem will report it as valid and hand the handler a `WebhookMetadata` claiming that data belongs to the victim shop.

### Impact Explanation
This directly maps to the analog class "a shop authenticated versus the shop stored/acted upon differs" — the HMAC only authenticates the body bytes, not the shop identity claim. A host application that keys its persistence, business logic, or session lookup off `WebhookMetadata#shop` (which is the documented, intended way to consume webhook data via this gem's `WebhookHandler` interface) can be made to attribute attacker-supplied webhook data to an arbitrary victim shop domain, since the gem itself asserts the request is "valid" (`Utils::HmacValidator.validate` returns true) even though the shop field was never verified. This is a cross-tenant identity-binding failure inside the gem's own webhook-verification code path, not merely the host ignoring documented behavior — the gem's `process` method is what asserts authenticity and constructs the trusted `WebhookMetadata`.

### Likelihood Explanation
Exploitability is bounded by the attacker's ability to obtain one body+HMAC pair that validates for *any* shop (e.g., from their own installed instance of the app, since HMAC uses only `Context.api_secret_key`/`old_api_secret_key`, both process-global secrets, not per-shop). Because the signature never binds to shop identity, once a valid `(body, hmac)` pair is known for a given payload shape, the `shop-domain` header can be freely swapped to target any other shop without invalidating the signature. No access token, session, or victim-specific secret is required — only the app's single shared HMAC secret, which every installed shop's webhooks are signed with.

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, `api-version`, `webhook-id`) in the signable string used for HMAC computation/verification (or otherwise cryptographically bind them to the body, e.g. via Shopify's own signed headers if available), so that `Utils::HmacValidator.validate` fails whenever any of these values has been altered relative to what was actually signed by Shopify.

### Proof of Concept
1. App receives a legitimate webhook for `topic=orders/create`, body `{"id":1}`, with headers `x-shopify-shop-domain: attacker-shop.myshopify.com` and a valid `x-shopify-hmac-sha256` computed over `{"id":1}` using the app's shared secret (attacker owns this shop, so they legitimately receive this webhook).
2. Attacker resends the identical raw body and HMAC value to the app's webhook endpoint, but replaces the header with `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `request.to_signable_string` (the unchanged raw body) and succeeds: [5](#0-4) 
4. `Registry.process` builds `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body:, ...)` and invokes the app's handler with data now falsely attributed to the victim shop: [6](#0-5)

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-21)
```ruby
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
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
