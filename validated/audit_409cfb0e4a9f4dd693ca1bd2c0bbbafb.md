### Title
Webhook shop identity not bound to HMAC signature enables cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the unauthenticated `shop-domain` header to identify which merchant/tenant the webhook belongs to. Because the shop identity is never included in the HMAC-signed payload, any actor who obtains one valid `(body, hmac)` pair (e.g., from a webhook legitimately delivered to their own store) can replay that exact body/HMAC to the app's public webhook endpoint while substituting an arbitrary `shop-domain` header, causing the handler to process attacker-chosen data under a victim shop's identity.

### Finding Description
`Webhooks::Registry.process` verifies authenticity like this: [1](#0-0) 

The HMAC check delegates to `Utils::HmacValidator.validate`, which computes the signature over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only the raw body — the `shop` is read from a header that is completely outside the signed material: [3](#0-2) 

The identity binding the check is supposed to enforce is: `HMAC-covered bytes == bytes that determine which shop the webhook is attributed to`. In practice the equality is broken: `HMAC(raw_body) == valid` is checked, but `request.shop` (used downstream to attribute the webhook to a tenant in `WebhookMetadata`) comes from a header never included in `raw_body`. Any party capable of directly POSTing to the app's public webhook endpoint (this is an internet-reachable route, not one requiring Shopify's network) with a previously-observed valid `(body, hmac)` pair for topic X can freely choose the `shop-domain` header value and have the handler treat the payload as belonging to any shop. Since a merchant/attacker can legitimately trigger real webhook deliveries to their own store (and capture the raw bytes + HMAC, e.g. by controlling their own callback URL), they hold a valid signature they can then relay against a different shop identity — the check "verify the sender is authentic" is bypassed for the purpose of attributing data to another tenant, exactly analogous to the reported bug class where a validity check is satisfied via an indirect/alternate path rather than the intended one.

### Impact Explanation
This breaks the shop/tenant authentication boundary: the handler processes payloads believing they originate from and pertain to a specific merchant shop, when in fact only the body content (not the tenant identity) was ever verified. This enables cross-tenant data injection/attribution — an app that keys internal actions (e.g., updating stored per-shop data, triggering emails, syncing state) off `WebhookMetadata#shop` would perform those actions against the attacker-chosen victim shop using attacker-controlled webhook body content, matching the "cross-tenant access" critical impact category.

### Likelihood Explanation
Requires the attacker to (a) be able to reach the app's public webhook endpoint directly (true by design — it's a public HTTPS endpoint) and (b) possess one valid `(raw_body, hmac)` pair, which is straightforwardly obtainable by any user who owns a shop that has the app installed and can trigger/receive at least one real webhook delivery for a topic. No secret key, access token, or privileged account is required beyond ordinary merchant-level usage of the app.

### Recommendation
Bind the shop identity into the value that is HMAC-verified, e.g., include the `shop-domain` (and ideally `topic`, `webhook-id`) header values in `to_signable_string`, or independently re-validate that the header-derived shop matches a shop the app actually has an active session/installation for before processing. At minimum, document that `request.shop` is unauthenticated and must not be trusted for security-sensitive routing without additional verification (e.g., cross-checking against a known/installed shop list).

### Proof of Concept
1. App has webhook endpoint `POST /webhooks` wired to `ShopifyAPI::Webhooks::Registry.process`.
2. Attacker installs the app on their own shop `attacker.myshopify.com` and configures/observes a webhook delivery for topic `orders/create`, capturing the raw JSON body `B` and the valid `x-shopify-hmac-sha256` value `H` (computed by Shopify using the app's shared `api_secret_key` over `B`).
3. Attacker sends a new request directly to the app's public webhook endpoint:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: H
   x-shopify-shop-domain: victim-shop.myshopify.com
   Body: B
   ```
4. `Utils::HmacValidator.validate` recomputes HMAC over `B` only, which matches `H`, so the request passes validation in `Registry.process`.
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and processes attacker-supplied body content as if it came from the victim shop — corroborated by `Registry.process`'s use of `request.shop` immediately after the HMAC check succeeds: [4](#0-3)

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
