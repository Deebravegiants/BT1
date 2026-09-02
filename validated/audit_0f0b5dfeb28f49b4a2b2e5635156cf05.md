### Title
Webhook `shop` attribution is not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then unconditionally trusts the `shop-domain` header to attribute the event to a specific merchant. Because the `shop` value is never part of the signed material, an attacker who possesses any single valid `(body, hmac)` pair for the app (e.g. from their own shop's legitimately delivered webhook, since the app's `api_secret_key` is shared across all installs) can replay that exact body/HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header, and the library will report the event as authenticated and originating from the victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

The `shop`, `topic`, and `webhook_id` accessors are read directly from attacker-controllable HTTP headers and are never included in the signed string: [2](#0-1) 

`Utils::HmacValidator.validate` verifies only `verifiable_query.to_signable_string` against the HMAC, i.e. only the body for webhooks: [3](#0-2) 

`Registry.process` performs this HMAC check and, immediately afterward, hands `request.shop` to the app's handler as if it were authenticated together with the body: [4](#0-3) 

The identity binding that should hold is: `shop attributed to the event == shop whose secret produced the HMAC`. In reality the HMAC only proves `body == body signed with api_secret_key`; it proves nothing about which shop the header claims to be from. Since a single `api_secret_key` is shared by every shop that installs the app, any legitimately received webhook (body+hmac pair, obtainable by the attacker installing the app on their own store) remains HMAC-valid no matter which `shop-domain` header value accompanies it on replay.

### Impact Explanation
If the consuming application uses `WebhookMetadata#shop` (as passed straight through by `Registry.process`) to look up which merchant's session/data the event applies to — a documented, intended use of this field — an attacker can forge webhook events that are misattributed to a victim shop. This is a cross-tenant confusion: actions/state changes intended to be scoped to the attacker's own shop (or forged content entirely, within the same JSON schema) can be applied against another merchant's stored session/data, because the shop identifier delivered by the library is never bound to the HMAC that "authenticates" the call.

### Likelihood Explanation
Exploitation only requires posting an HTTP request to the app's public webhook endpoint with attacker-chosen headers and a previously-observed valid `(body, hmac)` pair — no access token, no `client_secret`, and no privileged account is needed. Obtaining one valid pair is trivial for any unprivileged internet user, since they can install the app on their own development/test store and receive a legitimately signed webhook.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signable string that the HMAC covers, or require the consuming application to cross-check `request.shop` against a known/installed shop list independently of the HMAC result before trusting it in `Registry.process`/`WebhookMetadata`.

### Proof of Concept
1. Install the app on shop `attacker.myshopify.com`; capture a real webhook delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(api_secret_key, B)`).
2. Replay to the app's webhook endpoint:
```
POST /webhooks
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: H
X-Shopify-Shop-Domain: victim.myshopify.com
Body: B
```
3. `Utils::HmacValidator.validate` returns `true` (body/HMAC unchanged), and `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: B, ...)`, causing the app to process the attacker's event as if it belonged to `victim.myshopify.com`.

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
