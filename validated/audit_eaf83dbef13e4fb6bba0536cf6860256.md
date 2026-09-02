I have enough evidence to confirm this vulnerability. The HMAC signature (`Request#to_signable_string`, line 36-38) covers only `@raw_body`, while `topic`, `shop`, `api_version`, and `webhook_id` are all read directly from unauthenticated HTTP headers (lines 15-33) and passed downstream to the handler as trusted values.

### Title
Webhook `shop` (and `topic`/`webhook-id`/`api-version`) header values are trusted despite not being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then unconditionally trusts the `shop-domain`, `topic`, `webhook-id`, and `api-version` values taken from HTTP headers to build the `WebhookMetadata` handed to the host application's handler. Because those header fields are not part of the signed content, the identity binding "authenticated webhook == data attributed to a specific shop" does not hold, breaking `request.shop (trusted) == request.shop (HMAC-verified)`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are read straight out of attacker-controllable HTTP headers with no cryptographic binding to the body or to the HMAC: [2](#0-1) 

`Registry.process` validates only the body-derived HMAC and then immediately trusts `request.shop`/`request.topic`/etc. to construct the metadata passed to the app's webhook handler: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (i.e., the raw body) and the app's `api_secret_key`: [4](#0-3) 

Because the signature is a function of body-only bytes, any `(raw_body, hmac)` pair that is valid for one shop is *also valid* for any other shop, topic, api_version, or webhook_id — those header values are never mixed into the signed material. An unprivileged internet user who can obtain one legitimate `(body, hmac)` pair (e.g., by installing the target app on their own store and observing a webhook delivery, since `api_secret_key` is shared across all merchants of a multi-tenant app) can freely replay that exact body+HMAC to the app's public webhook endpoint while substituting `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) with a victim shop's domain or an arbitrary attacker-chosen value. `Utils::HmacValidator.validate` still returns `true` because it never inspected those headers, and `Registry.process` dispatches the forged shop/topic straight to the host application's handler as if it were an authenticated fact.

### Impact Explanation
This breaks the identity binding "shop the handler acts on" == "shop the webhook was actually verified for," resulting in cross-tenant data/event forgery: an attacker can make the host application believe an event (order, uninstall, GDPR request, etc.) originated from an arbitrary shop domain of their choosing, while supplying attacker-controlled body content. Depending on how the host app's webhook handler uses `WebhookMetadata#shop` (e.g., looking up/mutating that shop's stored session, triggering data deletion, updating billing state), this enables cross-tenant access or corruption of another merchant's data — satisfying the Critical "cross-tenant access" bar.

### Likelihood Explanation
High. The webhook endpoint is a public HTTP endpoint by design (Shopify posts to it without further authentication). Obtaining one valid `(body, hmac)` pair only requires installing the app on an attacker-owned development store (a normal, unprivileged action for a public/multi-tenant app) and capturing a real webhook delivery; the same `api_secret_key` is used to validate every shop's webhooks, so the captured signature is portable across shop identities. No access token, `api_secret_key`, or privileged account is required.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, and ideally `webhook-id`/`api-version`) in the HMAC-signed material, or otherwise cryptographically bind them to the verified payload, so a captured `(body, hmac)` pair cannot be replayed against a different shop or topic than the one Shopify actually delivered it for.

### Proof of Concept
1. App installs itself (or is installed by the attacker) on an attacker-owned store `attacker-shop.myshopify.com`, which is authorized to receive real webhook deliveries signed with the app's shared `api_secret_key`.
2. Attacker captures a legitimate webhook POST, e.g. body `{"id":1,...}` with header `X-Shopify-Hmac-Sha256: <valid-hmac-for-body>` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker resends the identical body and `X-Shopify-Hmac-Sha256` value to the same public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally changes `X-Shopify-Topic`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the raw body against the HMAC: [5](#0-4) 
5. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: <attacker body>, ...)`, i.e., the app processes attacker-controlled data as if it belonged to `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
