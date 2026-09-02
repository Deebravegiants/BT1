This confirms the finding. The docs explicitly state that `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" based on the HMAC, and pass `data.shop` (the shop domain) to the app's handler as trusted, authenticated data — but the HMAC computation itself never covers the shop domain header.

### Title
Webhook `shop` domain is not covered by HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the body only and then forwards `request.shop` straight into `WebhookMetadata` as trusted tenant identity, without any cross-check that the signed payload actually belongs to that shop.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` and compares it to the received `hmac` value using `OpenSSL.secure_compare`. [1](#0-0) 

For webhooks, `to_signable_string` is defined to be only the raw JSON body (`@raw_body`), while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from HTTP headers that are never part of the signed content: [2](#0-1) 

`Registry.process` only calls `Utils::HmacValidator.validate(request)` (i.e. checks the body signature) and then unconditionally trusts `request.shop` to build `WebhookMetadata`, which is handed to the application's webhook handler as authoritative tenant context: [3](#0-2) 

Because Shopify apps use a single, shared `api_secret_key` (the app's client secret) across every merchant installation, any unprivileged internet user can install the target app on a shop they themselves control. Their own installation will receive genuinely HMAC-valid webhook deliveries (signed with the app's shared secret) for events they trigger in their own store (e.g., `orders/create`), with a body they can shape by controlling their own store's data. Since `shop` is not part of the signed content, that attacker can replay the exact `raw_body` + `x-shopify-hmac-sha256` pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks body bytes against the shared secret), and `Registry.process` dispatches the attacker-controlled body to the handler labeled as belonging to the victim shop. This breaks the identity binding `shop_used_for_authorization == shop_bound_by_hmac`, since the HMAC binds only to the body, never to the shop claimed in the headers.

### Impact Explanation
This is a cross-tenant vulnerability: an attacker who can install the app on any shop (which requires no special privilege — any merchant/developer can install a public Shopify app) can forge webhook events that the app's own handler will attribute to an arbitrary victim shop, with attacker-controlled body contents (subject to Shopify's schema for that topic). Depending on what the host app does with `data.shop` and `data.body` (e.g., updating order records, redacting/creating data, billing actions, GDPR compliance mandatory webhooks such as `customers/redact`), this can lead to cross-tenant data corruption or unauthorized actions performed against a victim merchant's account under a passed HMAC check that the library documents as proof the "request did indeed come from Shopify" for that shop.

### Likelihood Explanation
Likelihood is high for any app that is installable by multiple independent tenants (the standard Shopify public/custom app model): the attacker only needs their own legitimate installation of the target app to obtain validly-signed webhook bodies, then can replay them to the shared webhook endpoint with a forged shop header, since the endpoint accepts requests based purely on the HMAC-over-body check documented in `docs/usage/webhooks.md` ("This will verify the request did indeed come from Shopify").

### Recommendation
Bind the shop identity into the value that is actually verified. Include `shop` (and ideally `topic`/`webhook_id`) in the signable content covered by the HMAC, or otherwise cryptographically bind the `x-shopify-shop-domain` header value into the verification (e.g., by treating `to_signable_string` as `headers['shop-domain'] + raw_body` if Shopify's signing already covers it, or by cross-validating `request.shop` against session/install records prior to trusting it) before constructing `WebhookMetadata` in `Registry.process`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and receives a webhook, e.g. `orders/create`, whose body they control the content of (by creating a crafted order).
2. Shopify signs the delivery: `hmac = HMAC-SHA256(shared_api_secret_key, raw_body)`, delivered with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <hmac>`.
3. Attacker captures `raw_body` and `x-shopify-hmac-sha256`, then sends a new POST to the app's public webhook endpoint reusing the same `raw_body`/`hmac`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers; `Utils::HmacValidator.validate(request)` recomputes HMAC over `raw_body` only (`to_signable_string`), matching the replayed hmac — validation passes.
5. `Registry.process` invokes `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: attacker_controlled_body, ...))`, and the application processes attacker-controlled data as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
