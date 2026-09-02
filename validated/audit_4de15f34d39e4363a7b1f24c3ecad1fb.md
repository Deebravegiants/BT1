## Title
Webhook `shop` domain is trusted for tenant attribution but is not covered by the HMAC signature, enabling cross‑tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the handler a `shop` value taken from an HTTP header that is never included in the signed material. Any party able to obtain one genuine, HMAC‑valid webhook payload for their own tenant (e.g. by installing the app on their own store) can replay that exact body to the shared webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header, and the request still passes signature verification.

### Finding Description
The HMAC check is performed against `to_signable_string`, which for webhooks is defined as just the raw body: [1](#0-0) 

The `shop` accessor, however, is read from an unauthenticated header and is not part of that signed string: [2](#0-1) 

`Registry.process` validates only the HMAC and then forwards `request.shop` directly to the application's webhook handler as the authoritative tenant identifier, without any binding between the two: [3](#0-2) 

`HmacValidator.validate` computes the signature purely over `verifiable_query.to_signable_string` (i.e. the raw body for webhooks) and compares it to the received HMAC — it has no knowledge of, or dependency on, the `shop` header: [4](#0-3) 

This breaks the identity binding: `shop (used to attribute the event to a tenant) == shop (covered by the HMAC that authenticates the request)`. The equality does not hold — the header can be swapped for any string while the HMAC remains valid, because it was computed independently of that header.

### Impact Explanation
An attacker who is merely an unprivileged tenant of the multi‑tenant app (e.g. installs the app on a free/dev store they control) can capture one legitimate webhook delivery (valid body + valid `x-shopify-hmac-sha256`) sent to the app's shared webhook endpoint. They can then send that identical body/HMAC pair directly to the same endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header rewritten to any other merchant's shop domain. `Registry.process` will accept it as authentic and invoke the registered handler with `WebhookMetadata#shop` set to the victim's domain, causing the application to process attacker-controlled data as if it came from the victim tenant. Depending on how the host application keys business logic off `shop` (e.g. `app/uninstalled`, billing, GDPR, or data-sync webhooks), this enables cross-tenant data corruption, spoofed lifecycle events, or state confusion attributed to a shop the attacker does not control — a cross-tenant boundary violation.

### Likelihood Explanation
Exploitation requires only the ability to install/operate one's own tenant on the target app (a common, low-privilege capability for any Shopify merchant) and to send a crafted HTTP POST with a captured body/HMAC pair to the app's public webhook endpoint — no access to `api_secret_key` or any victim credential is needed, since the same shared secret is used to validate all tenants' webhooks and the shop header is not covered by that signature.

### Recommendation
Bind the `shop` (and other tenant/context identifying values) into the HMAC-signed material, or otherwise verify them independently against a source of truth the app controls (e.g. the shop the webhook was registered for in `Registry`), rejecting webhooks whose header-derived shop cannot be corroborated. At minimum, document and enforce that `request.shop` must never be trusted for tenant attribution without cross-checking it against known/registered shops for the topic/subscription.

### Proof of Concept
1. Install the target app on attacker-controlled store `attacker-shop.myshopify.com`, receive any real webhook (e.g. `orders/create`) at the app's shared endpoint. Capture the raw body `B` and the header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(api_secret_key, B)`).
2. Send a new POST to the same webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` unchanged, and `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` recomputes `HMAC(api_secret_key, B)` — this equals `H` regardless of the shop header, so validation succeeds: [3](#0-2) 
4. The registered handler executes with `data.shop == "victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's own store.

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
