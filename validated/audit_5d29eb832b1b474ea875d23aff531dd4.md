### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) that is handed to the application's webhook handler from the `x-shopify-shop-domain` HTTP header, but the HMAC signature that `ShopifyAPI::Webhooks::Registry.process` verifies only covers the raw request body. The `shop` field — the value host apps use as the tenant/session key when processing the webhook — is not bound by the cryptographic signature at all.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Registry.process` validates the webhook exclusively via `Utils::HmacValidator.validate(request)`, which computes/compares the HMAC over that signable string [2](#0-1) [3](#0-2) . Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic coverage [4](#0-3) . After a valid HMAC check passes, `Registry.process` builds the metadata object passed to the app's handler directly from `request.shop` [5](#0-4) .

This breaks the intended identity binding: `hmac(raw_body) == valid` should imply `shop == the tenant whose data produced raw_body`, but the equality actually verified is only `hmac(raw_body) == valid`; `shop` is an independent, attacker-controllable header value. Any party who can obtain one authentic `(raw_body, hmac)` pair — trivially available to any merchant/developer who installs the app on their own store and lets it receive a real webhook — can replay that exact body/HMAC pair while substituting an arbitrary `x-shopify-shop-domain` header (e.g. a victim's shop domain). The signature still validates because it never covered the header, so `Registry.process` invokes the handler with attacker-chosen `data.shop`.

### Impact Explanation
Any host application that uses `WebhookMetadata#shop` to key session/access-token lookups, write per-tenant data, or make follow-up Admin API calls on behalf of "the shop identified by the webhook" is exposed to cross-tenant data confusion: an authenticated-looking webhook (valid HMAC) can carry a spoofed shop identity, letting one tenant's attacker cause the app to act as if the event came from a different, victim tenant. This matches the "Critical - cross-tenant access" impact category, since the gem itself is the one exposing an unauthenticated field as the trust anchor for tenant identity.

### Likelihood Explanation
The prerequisite (obtaining one genuine `raw_body`/HMAC pair) is trivial for any unprivileged party who can install the app on a shop they control — no privileged credential, `api_secret_key`, or access token of the victim is required. Replaying HTTP requests with modified headers is standard, low-effort tooling (curl/Burp). The only remaining question is whether a given host application actually relies on `data.shop` for tenant-sensitive decisions, which is common and encouraged by the gem's own `WebhookMetadata` design.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) header value inside the HMAC-covered signable string, or otherwise cryptographically bind the header claims to the body before trusting them — e.g., have `Request#to_signable_string` canonically incorporate `shop`, or require the host app to cross-check `request.shop` against a session store keyed by data independent of the header. At minimum, document that `request.shop`/`WebhookMetadata#shop` is unauthenticated and must not be used as a sole tenant key.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker.myshopify.com`; trigger any webhook topic the app subscribes to, capturing the raw POST body and its `x-shopify-hmac-sha256` header — both are valid because the attacker's shop genuinely produced this payload.
2. Replay the exact same body and HMAC header to the app's webhook endpoint, but replace `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds (it only checks `raw_body` against the HMAC) [6](#0-5) , so `Registry.process` calls the registered handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"` [7](#0-6) , even though none of the payload actually originated from that shop.

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
