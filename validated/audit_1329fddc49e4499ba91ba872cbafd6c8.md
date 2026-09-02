### Title
Webhook `shop` (and other identifying headers) are not covered by the HMAC signature, allowing tenant-header forgery on an otherwise valid webhook - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw body, then forwards the `shop` (and `topic`/`webhook_id`) values taken directly from unauthenticated HTTP headers to the application's handler as the tenant identity. Because these headers are not part of the HMAC-covered bytes, an attacker who can produce (or replay) a request with a valid body/HMAC pair can set an arbitrary `shop` header, breaking the binding between "bytes verified" and "bytes acted on."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `Request#shop`, `#topic`, and `#webhook_id` are read straight from HTTP headers with no cryptographic binding to the body or to the HMAC: [2](#0-1) 

`Registry.process` validates only the HMAC (which covers the body) and then unconditionally trusts `request.shop`/`request.topic`/`request.webhook_id` to build the `WebhookMetadata` handed to the app's business logic: [3](#0-2) 

The equality the gem is implicitly promising is: `bytes_verified_by_HMAC == bytes_the_handler_acts_on`. In reality: `bytes_verified_by_HMAC = raw_body` while `bytes_the_handler_acts_on = raw_body ∪ {shop, topic, webhook_id headers}`. This is structurally identical to the report's `chainId[collateralId]` vs. `chainId[debtId]` mismatch: the check (HMAC validity) is performed over one identity-relevant surface, while the code acts on a broader surface (headers) that is not covered by that check, so the check answers permissively for data it never inspected.

### Impact Explanation
If the host application (as most integrations do, mirroring the gem's own test suite, e.g. `test/webhooks/registry_test.rb`) uses `WebhookMetadata#shop` to select the tenant/session/database row to update, an attacker who can obtain any single valid `(body, hmac)` pair for their own shop (e.g., by triggering a webhook to their own installed app, which is not a privileged action) can replay that exact body/HMAC while substituting a different `shop` header. `HmacValidator.validate` will still return true because it only re-derives the HMAC from `to_signable_string` (the body) and compares it—it never binds the `shop` header into the signature: [4](#0-3) 

This can produce cross-tenant data processing: a webhook payload that legitimately belongs to shop A is processed by the handler as if it belonged to attacker-chosen shop B (or vice versa), since `process` never checks `request.shop` against anything.

### Likelihood Explanation
Exploitation requires only the ability to send an HTTP request to the app's public webhook endpoint with a previously-observed or self-generated valid `(raw_body, hmac)` pair (obtainable, e.g., from the attacker's own shop) and to modify only the `shop-domain` header before replay—no access token, `api_secret_key`, or privileged account is required. This is directly reachable through the gem's documented `Registry.process` entry point used by every embedding application.

### Recommendation
Bind the tenant-identifying fields into the authenticated payload rather than trusting bare headers: either include `shop`, `topic`, and `webhook_id` in the HMAC-signed string (`to_signable_string`), or require callers to independently verify `request.shop` against a known/expected shop for the delivery before invoking the handler, and document this requirement prominently since `Registry.process` currently gives no such guarantee.

### Proof of Concept
1. Attacker's own shop `attacker.myshopify.com` receives a legitimate webhook delivery: body `B`, header `x-shopify-shop-domain: attacker.myshopify.com`, HMAC `H = HMAC_SHA256(secret, B)`.
2. Attacker replays the request to the app's webhook endpoint with the same body `B` and same HMAC `H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `HmacValidator.validate` recomputes `HMAC_SHA256(secret, B)` (per `hmac_validator.rb:27-31`), which still equals `H`, so validation passes.
4. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...)` (per `registry.rb:198-199`) and invokes the app's handler, which processes attacker-controlled data as belonging to `victim.myshopify.com`.

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
