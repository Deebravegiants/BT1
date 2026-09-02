### Title
Webhook `shop` field trusted for tenant routing while excluded from the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` reads `shop`, `topic`, `webhook_id`, and `api_version` directly from unauthenticated HTTP headers, but the HMAC signature that `Registry.process` validates covers only the raw JSON body. This breaks the identity binding that the webhook signature is supposed to guarantee: `hmac(raw_body) == received_hmac` does not imply `shop_header == shop_that_produced_this_body`. An unprivileged holder of one genuine webhook (body + valid HMAC) for their own shop can replay it against the same app endpoint with a substituted `shopify-shop-domain` header and have it processed as if it belonged to another tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are pulled straight from HTTP headers with no cryptographic binding to the body: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` (i.e., the raw body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` accepts the request once this body-only HMAC check passes, and then forwards the **unauthenticated** `request.shop` value straight to the handler as the tenant identifier: [4](#0-3) 

The documented handler contract explicitly tells integrators to use `data.shop` to route/attribute the webhook to a tenant (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`): [5](#0-4) 

**Binding that should hold, but doesn't:**
`shop_header == shop_that_the_signature_actually_authenticates`

Before the request sequence: the HMAC is defined as a function of `raw_body` alone, and Shopify signs each webhook using `HMAC(body, api_secret_key)` for a specific shop/body pair.
After the attacker's request sequence: an attacker who is a legitimate merchant/installer of the app (an "unprivileged internet user" relative to other tenants) receives one genuine webhook for their own shop — a valid `(raw_body, hmac)` pair. They can re-POST this exact `raw_body`/`hmac` pair to the app's public webhook endpoint while changing only the `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) header to a different, victim tenant's domain. `HmacValidator.validate` still succeeds because it only checks `raw_body` against `hmac`; `Registry.process` then hands the handler `WebhookMetadata` with `shop` = victim's domain and `body` = attacker's own data.

This is exactly the report's bug class: a field that is *acted upon* (used for tenant identification/data routing) but *not covered* by the message authentication code, allowing the attacker to swap in an address/identity that was never verified — analogous to `SmartVaultV4::autoRedemption` receiving the vault address where the swap router address should have been passed.

### Impact Explanation
If the host application follows the gem's own documented pattern and uses `data.shop` to select which tenant's records to update (which is the explicitly documented, intended use of this field), an attacker who legitimately controls one shop/install of the app can inject attacker-controlled webhook data that the app will process and attribute to an arbitrary different shop domain string. This crosses a tenant boundary using only capabilities available to any ordinary app installer, meeting the "cross-tenant access" Critical-impact bar, since the shop identity binding — the very thing the HMAC exists to protect — is not actually enforced for the header-derived fields.

### Likelihood Explanation
Likelihood is meaningfully constrained by the host application's design; it is only exploitable if the host app trusts `data.shop` for tenant identification without independently re-validating it against its own webhook subscription state (e.g., correlating `webhook_id` with a specific shop from Shopify's registration side) — which is exactly what the gem's own documentation instructs developers to do. Because the vulnerable pattern is the gem's own recommended usage (`data.shop` for routing) and the replay requires only a single genuine `(body, hmac)` pair that any app installer already possesses for their own shop, likelihood is high for apps that follow the documented pattern verbatim.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) header values in the signable string that `HmacValidator` verifies, or otherwise cryptographically bind them to the body before exposing them to handlers — e.g., extend `VerifiableQuery#to_signable_string` for `Webhooks::Request` to canonicalize and include the shop/topic headers alongside the raw body, so that `Registry.process` rejects any request where these headers have been altered independently of the signed payload.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com`; attacker (as their own store's controller) triggers a webhook (e.g. `orders/create`) and captures the resulting HTTP request Shopify sends to the app's webhook endpoint, including headers `x-shopify-hmac-sha256: <H>` and body `B`.
2. Attacker re-sends an HTTP POST to the same app webhook endpoint with:
   - Body: unchanged `B`
   - Header `x-shopify-hmac-sha256: <H>` (unchanged)
   - Header `x-shopify-shop-domain: victim-shop.myshopify.com` (changed)
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: modified_headers)` builds successfully (required headers still present).
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(B, secret)` and compares to `<H>` — this still matches because `to_signable_string` only returns `B`: [6](#0-5) 
5. Validation passes; the handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`, i.e., attacker-originated data now attributed to `victim-shop.myshopify.com` in any app logic keyed off `data.shop`.

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

**File:** docs/usage/webhooks.md (L19-30)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
