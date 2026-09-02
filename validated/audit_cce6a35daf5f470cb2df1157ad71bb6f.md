### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop` value used by the library to identify which tenant a webhook belongs to is read from the unauthenticated `x-shopify-shop-domain` HTTP header. Because the app's webhook HMAC secret (`Context.api_secret_key`) is shared across every shop that installs the app, any shop can obtain a validly-signed `(body, hmac)` pair from its own genuine webhook traffic and replay it with a forged `shop-domain` header claiming to be a different, victim shop. The library's HMAC check will pass because it only verifies the body bytes, breaking the intended binding between "HMAC-verified request" and "shop the request claims to be from."

### Finding Description
`Webhooks::Registry.process` authenticates an inbound webhook purely via: [1](#0-0) 
which calls `Utils::HmacValidator.validate(request)`. That validator computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` header value: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` is defined as just the raw body: [3](#0-2) 

Meanwhile, `shop` — the value the library treats as the tenant identifier and hands to the webhook handler — is read directly from the `x-shopify-shop-domain` / `shopify-shop-domain` header, which is not part of the signed payload at all: [4](#0-3) 

After HMAC validation succeeds, `process` passes this unauthenticated `request.shop` straight to the app's handler as the tenant identity: [5](#0-4) 

The equality this breaks: `shop value cryptographically bound by HMAC == shop value acted upon by the handler`. In this code path that equality never holds — the signature says nothing about which shop's header value is attached to it.

Because a single app has one `api_secret_key` shared by all shops that install it, a legitimate installer (any unprivileged internet user who installs the app on their own store, i.e. no special privilege beyond normal app installation) can capture one authentic `(raw_body, hmac)` pair from a genuine webhook Shopify sends to their own shop, then submit that exact body/hmac pair to the app's webhook endpoint again with an attacker-chosen `x-shopify-shop-domain` header value naming a different, victim shop. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` will invoke the handler with `WebhookMetadata.new(shop: <victim_shop>, ...)`, i.e. data that is really the attacker's own is now attributed to the victim tenant.

### Impact Explanation
This crosses the tenant boundary the HMAC is meant to enforce: it allows an attacker who is merely one installer of a multi-tenant app to inject webhook events under an arbitrary other shop's identity into the host application via this gem's `Webhooks::Registry.process`/`Webhooks::Request` API. Any app logic that trusts `WebhookMetadata#shop` (or `request.shop`) to select per-tenant state, without additional shop-membership checks, can be manipulated cross-tenant — e.g. writing/mutating data keyed to a shop the attacker does not control. This matches the Critical "cross-tenant access" impact category, since it stems directly from a signature/identity-binding gap in the gem's own `to_signable_string`/`shop` implementation, not from the host ignoring documented behavior.

### Likelihood Explanation
Likelihood is moderate-to-high in any application with more than one installed shop: the only precondition is that the attacker (or an attacker-controlled shop) installs the app once to obtain one genuine `(raw_body, hmac)` sample, which is normal, unprivileged use of the app. No secret material, TLS interception, or elevated access is required — just replaying an HTTP POST with a substituted header.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the signed material the gem checks, or otherwise cryptographically bind the header-derived `shop` value to the verified body before it is handed to handlers — e.g., have `HmacValidator`/`Request` require that the `shop` used downstream matches a shop value embedded in and covered by the signed payload, or validate at the transport layer that the header's shop is consistent with a per-shop secret/session rather than the shared `api_secret_key`.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` and on victim `victim-shop.myshopify.com`; both share the same `Context.api_secret_key`.
2. Attacker triggers any webhook event on their own shop and captures the raw POST body and the `x-shopify-hmac-sha256` header Shopify sent them — this is a validly-signed `(body, hmac)` pair.
3. Attacker replays that exact body and `hmac` header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `request.to_signable_string` (`@raw_body`) — validation succeeds.
5. `process` invokes the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's data>, ...)`, i.e. the app now believes attacker-controlled webhook data originated from the victim shop. [5](#0-4) [6](#0-5)

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
