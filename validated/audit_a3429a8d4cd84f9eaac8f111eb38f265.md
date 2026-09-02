## Analog Found: Webhook identity fields excluded from HMAC verification

### Title
Webhook `shop`, `topic`, and `webhook_id` are trusted from unauthenticated headers while HMAC only binds the raw body - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` but its `to_signable_string` returns only the raw request body, so the HMAC verification performed by `Utils::HmacValidator.validate` never binds the `shop`, `topic`, `webhook_id`, or `api_version` values that are read from separate, unauthenticated HTTP headers. `Registry.process` uses these header-derived values directly to build the data handed to the app's webhook handler.

### Finding Description
The identity binding that should hold is:
`shop/topic/webhook_id (authenticated by HMAC)` == `shop/topic/webhook_id (used to dispatch the webhook to the handler)`

In the current implementation this equality is never enforced, because:

- `hmac` is computed from the `shopify-hmac-sha256` header [1](#0-0) 
- `to_signable_string` returns only `@raw_body` — none of `topic`, `shop`, `webhook_id`, `api_version` are part of the signed material [2](#0-1) 
- `shop`, `topic`, `webhook_id`, `api_version` are all read straight from separate headers with no cryptographic linkage to the body/HMAC [3](#0-2) 
- `Utils::HmacValidator.validate` only ever checks `verifiable_query.hmac` against `verifiable_query.to_signable_string`, i.e. only the body [4](#0-3) 
- `Registry.process` raises only if the body HMAC is invalid, then immediately trusts `request.shop` and `request.topic` to dispatch to the handler [5](#0-4) 

Because Shopify apps use a single, app-level `client_secret` shared across every shop that installs the app (not a per-shop secret), any shop that has legitimately installed the app receives real webhook deliveries with a valid `(raw_body, hmac)` pair signed with that same shared secret. Since the HMAC never binds `shop-domain`/`topic`/`webhook-id`, a party in possession of one legitimately-received `(raw_body, hmac)` pair can resend it to the app's public webhook endpoint with the `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) headers swapped to a different shop or topic, and `HmacValidator.validate` will still accept it as valid, because it only checks the body.

### Impact Explanation
This breaks the tenant isolation the app relies on: the handler receives `WebhookMetadata` claiming `shop: <victim-shop>` while the body content actually belongs to a different shop. Depending on how the host app uses `data.shop` (e.g. to select which merchant's DB record to update, or to route the payload into per-tenant processing), this allows cross-tenant data injection/confusion — attacker-controlled data (their own webhook payload) can be attributed to another tenant purely by resending it with a spoofed `shop-domain`/`topic` header. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Requires the attacker to have received at least one legitimate webhook for a shop under the target app (any shop that installs the app can do this — no leaked secret, access token, or privileged account required), and the ability to POST to the app's public webhook endpoint with arbitrary headers, both of which are ordinary capabilities of any merchant/attacker who installs a target public app. No TLS interception, secret leakage, or code changes on Shopify's side are needed.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed/verified material (or otherwise independently authenticate them, e.g. by validating the shop domain against the caller's own known-installed-shop records and rejecting mismatched topic/shop combinations) rather than trusting header values not covered by the HMAC.

### Proof of Concept
1. App shop A (attacker-controlled/legitimate installer of target app) receives a real webhook: headers include `x-shopify-hmac-sha256: <valid-hmac-for-body>`, `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-topic: orders/create`, body `{"id":1,...}`.
2. Attacker resends the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` at [6](#0-5)  passes because it only checks the body HMAC.
4. `Registry.process` dispatches `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: ...)` to the app's handler, which now processes attacker-supplied data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
