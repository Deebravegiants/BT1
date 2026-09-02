This confirms the finding. The docs explicitly state (`docs/usage/webhooks.md:125`) that `Registry.process` "will verify the request did indeed come from Shopify" based on the `data.shop` field being trustworthy, but the `shop` value is read from an unauthenticated HTTP header while the HMAC only covers the raw body.

### Title
Webhook shop-domain spoofing via replay: HMAC covers only the request body, not the `shopify-shop-domain` header, breaking the shop-identity binding trusted by handlers - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop` by reading the `shopify-shop-domain`/`x-shopify-shop-domain` header directly, but `to_signable_string`, which is what `HmacValidator.validate` verifies against `hmac`, is defined as `@raw_body` only. The HMAC therefore authenticates the body but not the shop-domain header, breaking the intended binding `authenticated_shop == shop_acted_on`.

### Finding Description
`Registry.process` treats a request as genuinely originating from Shopify for a specific shop once `Utils::HmacValidator.validate(request)` succeeds: [1](#0-0) 
`HmacValidator.validate` computes and compares the HMAC solely from `verifiable_query.to_signable_string`: [2](#0-1) 
For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`, while `shop` (and `topic`, `webhook_id`, `api_version`) are pulled from HTTP headers that are entirely outside the signed material: [3](#0-2) 
Because the `shop` header is never included in the HMAC-verified bytes, an unprivileged internet user who has legitimately received one valid `(raw_body, hmac)` pair for a webhook — e.g., by installing the app on their own shop and triggering an event — can replay that exact body and HMAC to the app's public webhook endpoint while substituting a different `shopify-shop-domain` header for a victim shop. `HmacValidator.validate` still succeeds because it never inspects the header, so `Registry.process` dispatches the handler with `WebhookMetadata.shop` set to the attacker-chosen victim shop: [4](#0-3) 
The documentation explicitly tells integrators that `process` "will verify the request did indeed come from Shopify," implying the entire `data` (including `shop`) is trustworthy once validation passes: this is not the case for the `shop` field. [5](#0-4) 

### Impact Explanation
This crosses a tenant boundary: an attacker-controlled body (from the attacker's own shop) is delivered to the application's handler tagged as belonging to a victim shop. Applications following the documented contract (`data.shop`) use this value to key session/data lookups (as shown in the documented handler example passing `shop_domain: data.shop` to enqueue further work): [6](#0-5) . Depending on the host app's use of `data.shop`, this enables cross-tenant data corruption/confusion (e.g., writing attacker data into a victim's records, or triggering actions against the victim's stored access token using attacker-supplied payloads) without needing any of the victim's credentials.

### Likelihood Explanation
High for any app relying on the documented `WebhookMetadata.shop` value as an authenticated tenant identifier. No privileged credentials are required — the attacker only needs their own valid app install (unprivileged, self-service) to harvest a legitimate `(raw_body, hmac)` pair, then a single unauthenticated HTTP POST with a modified header to the target app's public webhook endpoint.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id/api-version) header values as part of the material verified by the HMAC comparison, or otherwise cryptographically bind the header-derived `shop` to the signed payload before trusting it. At minimum, `Webhooks::Registry.process` / `WebhookMetadata` should not present `shop` as verified/trusted unless it has been bound into the HMAC check, and the documentation should be corrected to clarify that only `raw_body` integrity is verified.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and registers for topic `orders/create`.
2. Shopify sends a legitimate webhook: `raw_body = B`, header `shopify-hmac-sha256 = H` (valid HMAC of `B` with the app's real secret), `shopify-shop-domain: attacker.myshopify.com`.
3. Attacker replays the exact same `B` and `H` to the app's public webhook endpoint, but sets `shopify-shop-domain: victim.myshopify.com`.
4. In `Webhooks::Request#hmac`/`#to_signable_string`, only `B` is used, so `HmacValidator.validate` returns `true` (`compute_signature(B, secret) == H`) regardless of the header value: [7](#0-6) .
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: parsed_body, ...))`, so the app's handler processes attacker-controlled body content believing it belongs to `victim.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
