Based on the analysis, I found a concrete finding that maps to the "field acted on but not covered by the HMAC" analog category from the rules.

### Title
Webhook shop/topic/webhook-id attribution is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, but the `shop`, `topic`, `webhook_id`, and `api_version` values that are handed to the application's handler are read from unauthenticated HTTP headers that are not included in the signed content at all.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines `to_signable_string` to return only `@raw_body`: [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors instead pull straight from HTTP headers with no cryptographic binding to the HMAC: [2](#0-1) .

`Registry.process` validates the webhook using exactly this HMAC-over-body-only check, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` (all unsigned) to build the metadata passed to the app-supplied handler: [3](#0-2) . The HMAC verification itself, in `HmacValidator.validate`/`validate_signature`, only ever checks `verifiable_query.to_signable_string` — the body — against the secret; it has no visibility into which shop or topic the caller claims the body belongs to: [4](#0-3) .

The security invariant that should hold is: `shop-that-produced-the-signed-bytes == shop-attributed-to-the-processed-webhook`. Because the `shop-domain` header sits outside the signed bytes, that equality is not enforced — the HMAC only proves "this body was signed with our secret at some point," not "this body belongs to the shop/topic named in these headers."

### Impact Explanation
Any unprivileged actor who can obtain one genuine `(raw_body, hmac)` pair — trivially available by installing the app on their own development/trial store and capturing the webhook Shopify sends them — can replay that exact body/HMAC pair to the target app's webhook endpoint while substituting arbitrary `x-shopify-shop-domain`, `x-shopify-topic`, and `x-shopify-webhook-id` header values. `Registry.process` will accept the HMAC as valid (since the body is unchanged) and dispatch the handler with attacker-chosen `shop`/`topic`/`webhook_id` metadata alongside the replayed body. This lets an outsider inject data cross-tenant into another shop's records, or trigger topic-specific business logic (e.g. GDPR `customers/redact`, `shop/redact`) under a victim shop's identity, without ever possessing the app's `client_secret` or any merchant credential — a cross-tenant confusion/injection vector reachable purely from the public internet.

### Likelihood Explanation
The attacker only needs: (1) their own installation of the target app (or any store on which the app is installed and that they control), from which they receive a legitimately HMAC-signed webhook body, and (2) the ability to POST to the app's public webhook endpoint with custom headers, which is exactly how the endpoint is meant to be reached from the internet. No secret material, session, or elevated privilege is required, making this readily reachable by any developer/tester of the ecosystem.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the signed material verified by `HmacValidator` (e.g., include them in `to_signable_string`, or separately verify them against a value obtained from an authenticated source such as a prior registration lookup) instead of trusting headers that sit outside the HMAC. At minimum, document that consuming applications must not treat header-derived `shop`/`topic` values as authenticated unless they perform additional verification (e.g., cross-checking against known registered webhook endpoints/subscriptions).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers a webhook event (e.g., `orders/create`), capturing the raw POST body `B` and the resulting `x-shopify-hmac-sha256` header value `H` that Shopify computed with the app's shared secret.
2. Attacker sends a new HTTP request directly to the app's public webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged, still valid because `HmacValidator` only checks the body), but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and/or `x-shopify-topic: shop/redact`.
3. `ShopifyAPI::Webhooks::Request.new` parses these headers, `HmacValidator.validate` succeeds because it only re-hashes `@raw_body`, and `Registry.process` invokes the registered handler with `shop: "victim-shop.myshopify.com"`, `topic: "shop/redact"` — data the app will treat as an authentic, attributable event for `victim-shop`, despite the actual signed payload having originated from the attacker's own shop.

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
