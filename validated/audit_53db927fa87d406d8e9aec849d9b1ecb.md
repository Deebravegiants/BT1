### Title
Webhook Shop Domain Is Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (tenant) identity used by the webhook handler comes from an unauthenticated HTTP header. Since a single app-level `api_secret_key` signs webhook bodies for *every* shop that has the app installed, an attacker who controls one shop (or who can otherwise obtain one validly-signed webhook body/HMAC pair from Shopify for their own store) can replay that exact body+HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. The HMAC check still passes because it never covers the shop field, so the app processes attacker-controlled webhook data under the victim shop's identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `Request#hmac` is derived purely from the `hmac-sha256`/`x-shopify-hmac-sha256` header: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to the signed body: [2](#0-1) 

`Registry.process` validates only the HMAC (over the body) and then trusts `request.shop` (and `request.topic`) to build the metadata handed to the app's handler: [3](#0-2) 

`HmacValidator.validate` (and the shared `VerifiableQuery` interface) only ever authenticates `to_signable_string`, i.e., the body — never the shop domain that identifies the tenant the data is attributed to: [4](#0-3) [5](#0-4) 

The broken identity binding, stated as an equality that should hold but does not:
`shop_that_produced_the_valid_HMAC == shop_attributed_to_the_processed_webhook`

Because Shopify signs webhooks with the app's single shared `api_secret_key` (not a per-shop secret), any shop with the app installed can generate a validly-HMAC'd body. That body/HMAC pair is then portable to any other shop's identity as far as this gem's verification logic is concerned, since the shop header sits entirely outside the signed content.

### Impact Explanation
This breaks the tenant (shop) boundary the gem is responsible for enforcing when handing webhook data to the host application: cross-tenant data injection. An attacker who has installed the app on their own store (or otherwise captured one legitimate signed webhook payload) can cause the host app to process attacker-chosen webhook payloads (e.g. `orders/create`, `customers/update`, or GDPR mandatory topics) as if they originated from an arbitrary victim shop that also has the app installed. Depending on what the host app does in its handler (updating per-shop records, triggering fulfillment, redacting/exporting data, etc.), this can lead to cross-tenant state corruption or disclosure — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
The prerequisite is only that the attacker has (or can obtain) one shop where the target app is installed and can trigger any webhook delivery with content they control — a routine, unprivileged capability for any merchant who installs a public app. No access token, `client_secret`, or leaked credentials are required; the attacker never needs the app's secret because they harvest a real, validly-signed webhook that Shopify itself sent them.

### Recommendation
Bind the tenant identity into the authenticated data before dispatching to handlers: verify that `request.shop` is included in the HMAC-signed payload (Shopify does not offer this natively for webhooks), or better, cross-check the header-derived `shop` against the shop associated with the store/session context that the app expects for that specific registered webhook/subscription, rejecting the request if it doesn't match a known, expected shop for the delivery. At minimum, document prominently that `request.shop`/`request.topic` are unauthenticated headers and must not be trusted for authorization decisions without an independent tenant check by the host application.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., updates a customer) so Shopify delivers a legitimately HMAC-signed webhook body `B` with signature `H = HMAC_SHA256(api_secret_key, B)` and header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker replays the request to the app's webhook endpoint, keeping body `B` and header `X-Shopify-Hmac-Sha256: H` unchanged, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `@raw_body` (`B`) and succeeds because `H` was valid for `B` all along: [6](#0-5) 
4. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body`, despite the payload never having been authenticated for that shop.

### Citations

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

**File:** lib/shopify_api/utils/verifiable_query.rb (L11-16)
```ruby
      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
    end
```
