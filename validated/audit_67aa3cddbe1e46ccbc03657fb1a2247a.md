I have confirmed the full path. The finding is validated: `WebhookMetadata.shop` is populated directly from an HMAC-uncovered header, and `Registry.process` performs no independent cross-check of the shop identity against the signed content.

### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `shop` value taken from the `X-Shopify-Shop-Domain` header — a field that is never included in the signed data — to build the `WebhookMetadata` handed to the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
and `#shop` is read straight from the `shopify-shop-domain` (or `x-shopify-shop-domain`) header with no further validation: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes the HMAC over `to_signable_string` (i.e. the raw body) with the app's shared `client_secret` and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` uses this validation result as the sole authentication gate, then forwards `request.shop` — the unsigned header value — into `WebhookMetadata`, which is the tenant identity the host app's `WebhookHandler#handle` implementation is expected to trust: [4](#0-3) [5](#0-4) 

The identity binding that should hold is: **shop authenticated by the HMAC == shop used as the tenant/session key**. Here that equality is broken — the HMAC only proves `raw_body` was produced with the app's `client_secret`; it proves nothing about which shop the request claims to be from. Since the app's `client_secret` (and thus the HMAC key) is identical for every shop that installs the app, any entity capable of causing the app to receive one legitimate webhook (e.g., an app-installing merchant triggering an event topic they subscribed to in their own store) obtains a `(raw_body, hmac)` pair that remains valid for that body/secret combination regardless of what `X-Shopify-Shop-Domain` header accompanies it. Replaying that same body+hmac with a different `X-Shopify-Shop-Domain` header naming a victim shop still passes `HmacValidator.validate`, and `Registry.process` will hand the handler a `WebhookMetadata` claiming to be from the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion: an unprivileged party who can get one authentic webhook delivered for their own shop can forge the tenant identity of subsequent webhook deliveries to any other shop known to them (shop domains are not secret). Host applications commonly use `WebhookMetadata#shop` as the primary key to look up/update/delete tenant records (e.g., processing `app/uninstalled`, `shop/redact`, `customers/redact`, or business-data webhooks) purely because the request passed HMAC validation. This can lead to a malicious merchant injecting spoofed lifecycle or data events attributed to a victim shop, corrupting or exfiltrating the wrong tenant's state.

### Likelihood Explanation
Requires only that the attacker has (or can obtain) at least one legitimate `(raw_body, hmac)` pair produced under the app's own `client_secret` — trivially available to any merchant who installs the app and can capture the webhook payload it sends to their own configured endpoint. No access to `client_secret`, an access token, or the victim shop is needed. The only "guess" is a victim's `myshopify.com` domain, which is not secret.

### Recommendation
Bind the shop identity into the signed material, or independently verify it. Options:
- Include the `shop-domain` header value in `to_signable_string`, or
- Require the caller to supply and validate the `shop` value against Shopify's `X-Shopify-Shop-Domain` in combination with a per-shop secret/session lookup (not the shared `client_secret`), or
- At minimum, cross-check `request.shop` against a known/expected shop for the given topic before dispatching to the handler.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` and registers a webhook for a topic the attacker can trigger from their own admin (e.g., a product update).
2. Attacker triggers the event, causing Shopify to POST to the app's webhook endpoint with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid hmac over raw_body>`, and some `raw_body`.
3. Attacker intercepts/replays this exact `raw_body` and `X-Shopify-Hmac-Sha256` value to the same endpoint, but substitutes `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` in [6](#0-5)  returns `true` because it only checks `raw_body` against the shared `client_secret`, ignoring the shop header.
5. `Registry.process` in [4](#0-3)  dispatches `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` to the app's handler, which processes the event as if it genuinely originated from the victim shop.

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
