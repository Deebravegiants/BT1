### Title
Webhook processing trusts the `shop-domain` header for tenant attribution while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC that is computed **only over the raw request body**, but the value used to attribute the webhook to a merchant/tenant (`shop`) is read from an HTTP header that is **not included in the signed content**. This breaks the identity binding "the shop that the app processes data for == the shop the signature actually authenticates," analogous to the reported multisig issue where an action (transaction execution) can be manipulated because sequencing/target data isn't bound to the approval.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the HMAC strictly against that signable string: [2](#0-1) 

`Registry.process` uses this same body-only HMAC to authenticate the request, and then, once validated, blindly trusts `request.shop` (read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, never covered by the signature) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The `shop` accessor is read straight from an unauthenticated header: [4](#0-3) 

Because `api_secret_key` is shared across every shop that installs the same app, any merchant that has legitimately installed the app receives real webhook deliveries — a valid `(raw_body, hmac)` pair signed with the app's own secret. That merchant (an "unprivileged internet user" relative to any other tenant of the app) can capture one of their own legitimate webhook deliveries and replay the identical `raw_body` + `hmac` to the app's webhook endpoint while substituting a different value in the `shop-domain` header (e.g., a victim shop's domain). `HmacValidator.validate` will still pass, because it only checks the body bytes, not the header. `Registry.process` will then dispatch to the app's handler with `shop: <victim domain>` even though the payload actually originated from the attacker's own shop, breaking the equality `shop authenticated (HMAC-covered bytes) == shop attributed to the data (header value)`.

### Impact Explanation
This is a cross-tenant integrity issue: an attacker with no special privileges beyond having installed the multi-tenant app can inject events "as" any other shop the app knows about, because the shop identifier is never part of the cryptographically verified content. Depending on what the host application does with `WebhookMetadata#shop` (persist orders, update tenant records, trigger tenant-specific side effects), this can lead to cross-tenant data corruption or forged actions attributed to a victim merchant.

### Likelihood Explanation
Any developer/merchant who has installed the target app (a very low bar — no admin, no leaked secrets, no token theft) can capture one legitimate webhook body+HMAC pair from their own shop and replay it with a modified `shop-domain` header value. No cryptographic material beyond publicly-observable webhook traffic to their own shop is required.

### Recommendation
Bind the shop identity to the signed content, or otherwise stop treating the `shop-domain` header as authenticated:
- Have `Request#to_signable_string` include the `shop` (and `topic`) values so they are covered by the HMAC, or
- Require/encourage host applications to cross-check `request.shop` against the shop tied to the webhook subscription (e.g., the webhook id fetched via `Registry.get_webhook_id`) rather than trusting the header verbatim, and document this requirement prominently since `Registry.process` currently does no such correlation.

### Proof of Concept
1. App merchant "attacker-shop.myshopify.com" installs the target Shopify app and legitimately receives a webhook delivery, e.g. `orders/create` with body `{"id":1}"` and header `x-shopify-hmac-sha256: <valid HMAC of body with app's api_secret_key>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the exact same body and HMAC value to the app's webhook endpoint, but changes only the header `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into a request object; `Utils::HmacValidator.validate(request)` succeeds because it only recomputes the HMAC over `raw_body`, which is unchanged (`lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
4. `Registry.process` proceeds and calls the registered handler with `shop: "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:188-200`), even though the data actually came from the attacker's own shop — demonstrating the broken binding.

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
