Confirmed — there's no additional binding check between the `shop` header and the HMAC-signed body anywhere in `Registry.process`. This confirms the finding.

### Title
Webhook `shop` field is not covered by HMAC verification, enabling shop-identity spoofing on replayed webhook payloads - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the `shop` (tenant identifier) is read from an HTTP header that is never included in the signed bytes. `Registry.process` trusts this unauthenticated `shop` value when dispatching to the app's webhook handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and the HMAC validator computes/compares the signature over that string alone: [1](#0-0) 

Meanwhile `Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is completely outside the HMAC coverage: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then forwards the header-derived, unauthenticated `shop` value straight into the handler's `WebhookMetadata` as the tenant identity for the event: [3](#0-2) 

This breaks the intended identity binding: `hmac(raw_body) == hmac(raw_body)` is verified, but the equality that actually matters for tenant isolation — `header["shop-domain"] == the shop that produced this signed body` — is never checked. Since the webhook HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is shared across *all* shops that install the app (it is not shop-specific), any shop that has installed the app can obtain a genuinely-signed `(body, hmac)` pair from Shopify for events on its own store, then replay that exact body+HMAC to the app's webhook endpoint with the `shop-domain` header rewritten to point at a victim shop. The signature still validates because it never covered the shop field, and the handler processes the payload as if it belongs to the victim tenant.

### Impact Explanation
This is a cross-tenant identity confusion: an app installed by two independent shops (attacker's own store and any other merchant) allows the attacker to inject events that the host application will attribute to a shop it doesn't control, because this gem never binds the header-derived `shop` to the HMAC-verified bytes. Depending on how the host app's `WebhookHandler#handle` uses `data.shop` (e.g., looking up which merchant's records to update/delete, as with the mandatory `shop/redact` or `customers/redact` topics), this can lead to cross-tenant data corruption or disclosure driven entirely by an unprivileged, independent Shopify merchant account — no access token, secret, or privileged account is required beyond installing the app on one's own store.

### Likelihood Explanation
Any internet user can create a Shopify store and install a public app to become a legitimate, low-privileged tenant, then trigger events (e.g. product/order create) on their own store to receive a genuinely-signed webhook body+HMAC pair from Shopify. Because the secret is shared across tenants and the `shop` header is unauthenticated, replaying with a modified header is a simple, deterministic HTTP replay requiring no additional secrets.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook-id`) header values in the HMAC-signable string, or otherwise cryptographically bind them to the verified payload, so that `Utils::HmacValidator.validate` fails if any of these values are altered independently of the signed body. At minimum, `Request#to_signable_string` in `lib/shopify_api/webhooks/request.rb` should incorporate the shop-domain header into what is verified.

### Proof of Concept
1. Attacker creates `attacker-shop.myshopify.com` and installs the target app, which is a legitimate but unprivileged install.
2. Attacker triggers an event (e.g. product update) causing Shopify to deliver a webhook to the app with a valid `x-shopify-hmac-sha256` header computed over the JSON body using the app's shared `client_secret`.
3. Attacker captures `(raw_body, hmac_header)` from that legitimate delivery.
4. Attacker POSTs the identical `raw_body` and `hmac_header` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) succeeds because it only checks the body bytes; `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) dispatches the handler with `shop: "victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's own shop.

### Citations

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
