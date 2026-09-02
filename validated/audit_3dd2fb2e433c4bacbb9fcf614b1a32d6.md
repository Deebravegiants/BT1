### Title
Webhook shop identity is not covered by HMAC verification, enabling cross-tenant webhook forgery via replay - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` (and `topic`, `webhook_id`, `api_version`) exclusively from HTTP headers, while the HMAC signature that `Utils::HmacValidator` verifies is computed only over the raw request body. `Webhooks::Registry.process` validates the HMAC and then unconditionally trusts the header-derived `shop` to build the data handed to the app's webhook handler. This breaks the identity binding `shop authenticated == shop acted upon`: the cryptographic check only proves body integrity, never that the `shop-domain` header belongs to that body.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from headers with no relation to the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC only over `verifiable_query.to_signable_string` (i.e. the body) and compares it to the `hmac-sha256` header value: [3](#0-2) 

`Webhooks::Registry.process` performs that HMAC check and then immediately trusts `request.shop`/`request.topic` (never re-validated or bound to the signed bytes) to construct the `WebhookMetadata` passed to the app-supplied handler: [4](#0-3) 

Because the signature only proves "this body was HMAC'd with the app's secret at some point," and the `shop-domain` header is completely outside that signed scope, any body+HMAC pair that was legitimately generated once (e.g., by installing the app on an attacker's own shop and capturing a real webhook delivery) remains valid when replayed with the `shop-domain` header changed to a victim shop. `HmacValidator.validate` returns `true` because it never inspects headers, and `Registry.process` will label the event as coming from the victim shop.

### Impact Explanation
This is a cross-tenant identity binding break in the gem's own webhook-authentication primitive: the equality the library is supposed to guarantee — `hmac-signed-payload's shop == request.shop-domain header` — never actually holds, since the header is not part of the signable string. An unprivileged attacker who can install the target app on their own (free/trial) shop can capture one valid `(body, hmac)` pair for any topic they can trigger (e.g. `app/uninstalled`, `customers/redact`, `orders/create`), then replay it to the app's single webhook endpoint with the `x-shopify-shop-domain` header set to a different, victim merchant's shop. The signature still validates, and the host application's handler executes attacker-chosen webhook data/topic attributed to the victim tenant — a cross-tenant data/identity confusion.

### Likelihood Explanation
Likelihood is bounded by needing to observe at least one genuine `(body, hmac)` pair, which is trivially obtainable by any developer/attacker who installs the target app on their own store (a normal, unprivileged action) and inspects the webhook delivery it receives — no leaked secrets, TLS interception, or privileged access is required. The replay itself is a normal unauthenticated POST to the app's public webhook route.

### Recommendation
Bind the header-derived identity fields into the signed material verified by `HmacValidator`, or otherwise cryptographically tie `shop-domain`/`topic`/`webhook_id` to the payload before trusting them (e.g., include the relevant headers in `to_signable_string`, or independently verify `shop` against Shopify via a side channel/session lookup instead of trusting the raw header value for tenant attribution).

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `app/uninstalled`), capturing the raw body and the `x-shopify-hmac-sha256` value Shopify sent.
2. Attacker POSTs the exact same body and `x-shopify-hmac-sha256` value to the same app endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) recomputes the HMAC over `to_signable_string` (the body only) and it matches, so validation passes.
4. `Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb`) builds `WebhookMetadata` with `shop: request.shop` = `"victim-shop.myshopify.com"` and invokes the app's handler, which now processes an `app/uninstalled` (or other) event as if it genuinely originated from the victim shop.

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
