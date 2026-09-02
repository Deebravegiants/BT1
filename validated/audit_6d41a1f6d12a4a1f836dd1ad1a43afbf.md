### Title
Webhook Shop Domain Spoofing via Unauthenticated Header Enables Cross-Tenant Webhook Injection - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identifier (`shop`) from the `x-shopify-shop-domain` HTTP header, but the HMAC signature computed by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body, never the headers. Any party who can obtain one validly-signed webhook body for the app (trivially available to any merchant who installs the app on their own store, since the app's `client_secret`/HMAC key is shared across every shop that installs it) can replay that body to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header and have it accepted as coming from a different, victim shop.

### Finding Description
The webhook signature verification binds only the request body: [1](#0-0) 

while the tenant-identifying `shop` accessor is read straight from an attacker-controlled header that is not part of the signed payload: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` (the raw body) and the app's `api_secret_key`, with no dependency on `shop`: [3](#0-2) 

`Registry.process` only checks that the HMAC is valid for the body; it performs no check that the `shop` header is consistent with anything else (there is nothing else to check it against, since shop isn't signed), and then forwards the attacker-controlled `shop` value straight to the app's handler: [4](#0-3) 

The gem's own documentation instructs integrators to trust `data.shop` as the tenant key for downstream processing (e.g., enqueuing per-shop jobs): [5](#0-4) 

Because `api_secret_key`/`client_secret` is one value per app and is identical for every shop that installs that app, any shop (including one an attacker legitimately installs the app on) can generate a validly-HMAC'd body and then send it to the shared webhook endpoint with a spoofed `x-shopify-shop-domain` header pointing at a different, victim shop. The gem accepts it as authentic and hands the spoofed shop identity to the handler, breaking the identity binding: **the shop authenticated by the HMAC (none) ≠ the shop the app acts on (`request.shop` from the unsigned header)**.

### Impact Explanation
This allows cross-tenant webhook injection: an attacker who is merely one of many merchants using a multi-tenant app can cause the app to process attacker-supplied webhook data (topic + body) under the identity of a different shop. Depending on how the host app uses `data.shop` (e.g., to look up/update per-shop records, enqueue background jobs keyed by shop, or trigger side effects), this can lead to cross-tenant data corruption or unauthorized actions attributed to a shop the attacker does not control — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is high for any multi-tenant app built on this gem following its documented pattern (trusting `data.shop`). The only prerequisite is that the attacker can install the app on a shop they control (a normal, unprivileged action for any merchant) to obtain a validly signed body/HMAC pair, then replay it with a different `shop` header value to the app's single shared webhook endpoint.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the signed payload verification, or otherwise cryptographically bind the header-derived shop to the specific installation/access token on file, rather than trusting an unauthenticated header. At minimum, `HmacValidator`/`Webhooks::Request` should require the caller to supply the expected shop (from the app's own session/installation lookup) and reject the webhook if it does not match `request.shop`, instead of exposing an unauthenticated `shop` value directly to handlers.

### Proof of Concept
1. Attacker installs the target multi-tenant app on their own shop `attacker.myshopify.com`, obtaining legitimate webhook deliveries from Shopify signed with the app's shared `client_secret`.
2. Attacker captures one such raw webhook POST, e.g.:
   ```
   POST /callback/orders/create
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-signature-for-body>
   x-shopify-shop-domain: attacker.myshopify.com
   Body: {"id": 1, "note": "attacker controlled"}
   ```
3. Attacker replays the exact same body and HMAC header, only changing:
   ```
   x-shopify-shop-domain: victim.myshopify.com
   ```
4. `HmacValidator.validate` recomputes the HMAC over the (unchanged) body using the app's shared secret and it matches, so `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) proceeds and calls the handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, even though Shopify never sent this webhook for `victim.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
