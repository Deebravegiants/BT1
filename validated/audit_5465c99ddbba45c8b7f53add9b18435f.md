### Title
Webhook `shop-domain`/`topic`/`webhook_id` headers are trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook by HMAC-verifying only the raw request body, then hands the caller-supplied `shop`, `topic`, `webhook_id` and `api_version` header values straight to the app's handler as trusted identity fields — even though none of those headers are covered by the HMAC computation.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` computes/compares the HMAC exclusively over that signable string [2](#0-1) . The `shop`, `topic`, `webhook_id`, and `api_version` values are all read directly from HTTP headers with no cryptographic binding to the body or its signature [3](#0-2) .

`Registry.process` uses exactly this unauthenticated `shop` value to build the trusted `WebhookMetadata` passed into the app's handler: [4](#0-3) 
`WebhookMetadata` is a typed struct whose `shop`/`topic`/`webhook_id` fields are meant to identify which tenant/event the payload belongs to [5](#0-4) .

The intended identity binding should be:
`HMAC_valid(raw_body) ⟺ (raw_body, shop, topic, webhook_id) all originated together from Shopify for that specific shop`

What the gem actually implements is:
`HMAC_valid(raw_body) ⟺ raw_body was signed with the app's api_secret_key` — with `shop`/`topic`/`webhook_id` completely unauthenticated.

Critically, `api_secret_key` is a single value shared by the whole app across every installed shop (it is not per-shop) — see how it is used identically for every session's OAuth/webhook validation in `Oauth.validate_auth_callback` [6](#0-5)  and in `HmacValidator.validate` [7](#0-6) . Because the same secret validates the body regardless of which shop it came from, an attacker who legitimately installs the app on a shop they control receives real Shopify webhooks (valid `raw_body` + valid HMAC computed with the shared `api_secret_key`). They can capture one such `(raw_body, hmac)` pair and resend it to the app's public webhook endpoint while forging the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header to name a victim shop. `Registry.process` will pass HMAC validation (the body/HMAC pair is genuinely valid) and will invoke the app's handler with `shop` set to the victim's domain and attacker-controlled `body` content, since the shop header is only used for routing/labeling and never checked against the HMAC.

### Impact Explanation
This breaks the shop-identity binding relied on by every app built on this gem: it allows cross-tenant injection of arbitrary webhook payloads attributed to a shop the attacker does not control, satisfying the "Critical - cross-tenant access" bar. An attacker can inject fabricated `orders/create`, `app/uninstalled`, or other events for a victim shop, causing the host application to act on forged data as if it came from Shopify for that tenant (e.g. corrupting the victim's stored order/customer records, triggering de-provisioning logic, etc.), all without needing the victim's credentials, access token, or `client_secret`.

### Likelihood Explanation
Likelihood is moderate: any actor can sign up for/install the app on their own store for free, which is enough to obtain valid `(raw_body, hmac)` pairs signed with the app's shared `api_secret_key`. From there, forging headers on a direct HTTP POST to the app's public webhook endpoint requires no special access — the endpoint is internet-reachable by design. The main constraint is that the attacker must produce a `raw_body` whose content is useful for the target shop (e.g., generic mandatory-topic payloads such as `shop/redact`), but exact-body replay against a chosen `shop` header is sufficient to demonstrate cross-tenant delivery.

### Recommendation
Do not trust the `shop`, `topic`, or `webhook_id` headers as authenticated identity — either:
1. Include the relevant headers (at minimum `shop-domain` and `topic`) in the HMAC-signed material used by `to_signable_string`, so the signature cryptographically binds body to shop/topic, or
2. Require the calling application to independently verify that the `shop` in the webhook matches a shop it has an active session/install record for before acting on the payload, and document this requirement clearly since `Registry.process` currently gives no such guarantee.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` (a shop they control) and lets it complete OAuth normally.
2. Attacker triggers a webhook event (e.g. `customers/data_request`) on their own shop and captures the raw POST body and the `X-Shopify-Hmac-Sha256` header sent by Shopify to the app's webhook endpoint. This HMAC is valid because it's computed with the app-wide `api_secret_key` [8](#0-7) .
3. Attacker resends the exact same body and `X-Shopify-Hmac-Sha256` header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the body against the shared secret [9](#0-8) .
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ...)` [10](#0-9) , causing the host application to process attacker-controlled webhook data as if it genuinely originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L33-40)
```ruby
        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** lib/shopify_api/auth/oauth.rb (L64-64)
```ruby
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
```
