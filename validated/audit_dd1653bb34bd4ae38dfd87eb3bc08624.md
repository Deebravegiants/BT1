### Title
Webhook shop identity is not covered by HMAC, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identifier (`shop`) from the unauthenticated `X-Shopify-Shop-Domain` header, while the HMAC signature verified by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body. Because the app's webhook signing secret (`api_secret_key`/`client_secret`) is shared across all shops that install the app, any merchant who has installed the app can capture one of their own validly-signed webhook deliveries and resend it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop's domain. The gem will accept the payload as valid (HMAC only checks the body) and hand it to the app's handler tagged as belonging to the victim shop.

### Finding Description
The identity binding that should hold is:
`shop bound by HMAC == shop the app acts on`

In this gem it does not hold. `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`#shop` simply reads the `shop-domain`/`x-shopify-shop-domain` header verbatim, with no cryptographic binding to the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it to the received `hmac-sha256` header — the shop domain never enters the signed message: [3](#0-2) 

`Webhooks::Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identifier passed to the app's handler: [4](#0-3) 

Since the webhook signing secret is the app's `client_secret`/`api_secret_key`, which is identical for every shop that has installed the app (not a per-shop secret), any installed merchant can:
1. Receive a legitimate webhook for their own shop (valid body + valid HMAC + their own `shop-domain` header).
2. Replay that exact `raw_body`/HMAC pair to the app's webhook endpoint, substituting an arbitrary `X-Shopify-Shop-Domain` header (e.g., a victim shop they don't own).
3. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` forwards `shop: request.shop` — now pointing at the victim tenant — to the handler.

This breaks the equality `authenticated_shop == acted_on_shop`. Before the attack, an app trusts `data.shop` from `WebhookMetadata` to select which merchant's session/data store to mutate. After the attack, the same trusted field can be attacker-controlled to point at a different tenant while carrying attacker-influenced (their own, but re-sent) body content.

### Impact Explanation
This is a cross-tenant integrity bypass: the webhook processing pipeline exposed by this gem allows an unprivileged app user (one with no special access to any other merchant) to make the app process webhook data under a foreign shop's identity. Because `WebhookMetadata#shop` is the primary key most integrating apps use to route the webhook body into per-tenant storage or side effects, an attacker can inject/replay data attributed to a shop they do not own, without needing the app's `api_secret_key`, an access token, or any other credential beyond being able to install the app for their own store and capture an HTTP payload flowing to their own endpoint. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for apps that build directly on `ShopifyAPI::Webhooks::Registry.process`/`Request` as documented: the vulnerable code path is exactly the one demonstrated in `docs/usage/webhooks.md`, requires only installing the app as an ordinary merchant, capturing one's own genuine webhook delivery (trivial, e.g., via a public endpoint or a local proxy), and replaying it once with a modified header — no cryptographic secret or privileged access is needed.

### Recommendation
Include the shop-domain header (and ideally the topic and webhook-id) as part of the signed content, or otherwise cryptographically bind them, before trusting `request.shop`. Since Shopify's outbound webhook signature format cannot be changed by the gem, at minimum the gem should document/require verifying `request.shop` against the shop actually associated with the session/store the app expects for that delivery (e.g., reject if `shop` is not a shop with an active, matching webhook registration/session), rather than presenting `request.shop` as an implicitly-trusted, HMAC-verified value in `WebhookMetadata`.

### Proof of Concept
1. App A is installed on both `attacker.myshopify.com` and `victim.myshopify.com`, sharing the same `client_secret` (`api_secret_key`) for webhook signing.
2. Shopify sends a legitimate webhook to App A's endpoint for `attacker.myshopify.com`:
   - Headers: `X-Shopify-Hmac-Sha256: <valid HMAC of body>`, `X-Shopify-Shop-Domain: attacker.myshopify.com`
   - Body: `{"id": 1, "note": "malicious payload"}`
3. Attacker intercepts this delivery to their own endpoint/proxy, then re-POSTs the identical body and HMAC header to the app's webhook route, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Utils::HmacValidator.validate` recomputes HMAC over `raw_body` only and matches, since the body/HMAC pair is unchanged.
5. `Webhooks::Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: "victim.myshopify.com", body: {"id"=>1, "note"=>"malicious payload"}, ...))`, and the app processes attacker-supplied data as if it originated from `victim.myshopify.com`.

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
