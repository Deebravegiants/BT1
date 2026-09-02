### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request **body**. The `shop`, `topic`, `webhook_id`, and `api_version` values — all taken from HTTP headers — are never included in the signed payload, yet they are trusted as-is and handed to the host application's webhook handler as the tenant identity. Any user who can obtain one genuine, validly-signed webhook body+HMAC pair (e.g., for their own shop, by installing the app) can replay that exact body/HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header, causing the host application to process the payload as if it originated from a different (victim) shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are parsed straight from headers, independent of the signed content: [2](#0-1) 

`Registry.process` validates only this body-scoped HMAC, then immediately trusts `request.shop`/`request.topic`/`request.webhook_id` to construct the `WebhookMetadata` delivered to the app's registered handler: [3](#0-2) 

`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header — for a `Request`, that signable string is the body only: [4](#0-3) 

The identity binding that should hold is:
`shop header value delivered to the app's webhook handler == shop that the HMAC-secret holder (Shopify) actually generated the event for`

Because the header is outside the HMAC's scope, that equality is not enforced anywhere in the gem. A user who has installed the app on their own shop receives genuine webhooks with a body and HMAC computed by Shopify using the app's real `api_secret_key`. Since the HMAC never covers the `shop-domain` header, that same (body, hmac) pair remains valid regardless of what `x-shopify-shop-domain` value is sent alongside it. Replaying it with a different shop header value passes `HmacValidator.validate` unchanged and reaches the host application's handler tagged with an attacker-chosen shop identity.

### Impact Explanation
This breaks the cross-tenant boundary the webhook system is meant to provide: the host application's webhook handler receives `WebhookMetadata#shop` as the authenticated tenant key (this is the documented and expected contract — `ShopifyAPI::Webhooks::Registry.process` is the library's authentication boundary for webhooks). An attacker who merely installs the app on their own store (no special privilege, no leaked secret, no access token) can forge events attributed to any other merchant's shop domain — e.g., spoofing `app/uninstalled`, `shop/update`, or GDPR-style topics for a victim shop — causing the host app to take tenant-scoped actions (deleting data, revoking access, mutating billing state) against the wrong tenant. This matches the Critical "cross-tenant access" impact category since it defeats the tenant-identity guarantee the library is relied upon to provide.

### Likelihood Explanation
Likelihood is high for any app that trusts `WebhookMetadata#shop` (the library's own passed-through value) as the tenant key without independently re-verifying shop ownership — which is the intended usage pattern shown in the library's own webhook handler examples. The only prerequisite is that the attacker has legitimately installed the app once (a normal, unprivileged merchant action) to harvest one valid (body, hmac) pair, and the ability to POST directly to the app's public webhook endpoint with custom headers.

### Recommendation
Bind the shop identity into the authenticated material before trusting it:
- Include `shop-domain` (and ideally `topic`/`webhook-id`) in the signed content checked by `HmacValidator`, or
- Cross-check the header-derived `shop` against an independently trusted source (e.g., verify the shop is a session/tenant the app has on record and reject if the specific webhook id has already been seen for a different shop), or
- At minimum, document/enforce that host apps must not treat `WebhookMetadata#shop` as authenticated without additional verification, and consider incorporating the shop domain into `Request#to_signable_string`'s HMAC comparison surface if Shopify's delivery contract allows it.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. `POST /webhooks` with body `{"id":123}`, headers including:
   - `x-shopify-hmac-sha256: <valid HMAC of the body>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-topic: app/uninstalled`
2. Attacker replays the exact same body and `x-shopify-hmac-sha256` value, but changes the header to `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` passes (it only checks the body against the HMAC) — see [5](#0-4) .
4. `Registry.process` dispatches to the registered `app/uninstalled` handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, causing the host app to act as though the victim shop uninstalled the app.

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
