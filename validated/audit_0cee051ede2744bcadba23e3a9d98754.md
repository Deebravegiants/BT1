## Title
Webhook `shop` and `topic` identifiers are trusted from unauthenticated headers while the HMAC only signs the raw body, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body alone, but the `shop` (and `topic`) values dispatched to the app's webhook handler are read directly from HTTP headers that are never included in that signature. Anyone able to produce a validly-signed webhook body for the shared app secret (e.g. an attacker who installs the app on their own shop and receives a genuine webhook) can replay that exact body/HMAC pair while swapping the `shopify-shop-domain` header to any other tenant, causing the receiving application to process attacker-controlled data as if it belonged to a different, victim shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers with no cryptographic binding to that body: [2](#0-1) 

`HmacValidator.validate` only checks the signature over `to_signable_string` (the body), using the app's `api_secret_key`, which is shared across every shop that installs the app: [3](#0-2) 

`Registry.process` then trusts `request.shop` and `request.topic` verbatim to route and label the payload passed to the merchant's handler: [4](#0-3) 

The identity binding that is broken:
`shop_that_signed_the_body == shop_the_handler_believes_sent_it` is **not enforced**. The HMAC only proves "this body was produced using this app's secret," not "this body came from shop X." Since the secret is shared across all shops that install the app, any user who can trigger a legitimate webhook for their own store (or capture one) possesses a body+HMAC pair valid for the app. They can then submit that same body+HMAC with a forged `x-shopify-shop-domain` (and/or `x-shopify-topic`) header pointing at a victim shop. `HmacValidator.validate` still returns `true` because it never inspects the header values, and `Registry.process` hands the forged `shop`/`topic` straight to the handler.

### Impact Explanation
This crosses a tenant boundary: a malicious but otherwise unprivileged app user (any merchant who installs the app) can cause the host application to process webhook data attributed to a different merchant's `shop`. Depending on how the host app's handler uses `WebhookMetadata#shop` (e.g., looking up/updating per-tenant records, cache keys, billing state, or triggering per-shop side effects), this can lead to cross-tenant data corruption or disclosure — the exact "cross-tenant access" class called out as Critical impact.

### Likelihood Explanation
Any actor who can install the app on their own store (or otherwise obtain one genuine, validly-signed webhook body for the app) can perform this attack with a single HTTP request to the app's public webhook endpoint, only needing to alter the `shopify-shop-domain` (and optionally `shopify-topic`) header. No access token, `api_secret_key`, or privileged account is required beyond being an ordinary app user.

### Recommendation
Include `shop` (and ideally `topic`) in the HMAC-signed content, or otherwise cryptographically bind the header-derived tenant identifier to the verified payload before it is handed to consumer code — e.g., validate that the resolved `shop` matches a shop the caller is currently authorized/known for, rather than trusting the header as-is once the body HMAC passes.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers (or waits for) a webhook, e.g. `products/update`, capturing the raw POST body and its `x-shopify-hmac-sha256` header (both are valid because they're signed with the app's shared `api_secret_key`).
2. Attacker replays the identical body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com` (and optionally changes `x-shopify-topic`).
3. `Webhooks::Request.new` parses these headers; `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` verifies only the raw body against the shared secret and returns `true`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the handler with `shop: "victim.myshopify.com"` and the attacker-controlled body, even though the payload actually originated from the attacker's own store — demonstrating the header/HMAC binding gap.

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
