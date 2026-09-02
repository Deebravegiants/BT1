This confirms the finding. The docs explicitly promote `data.shop` as a trustworthy field ("The shop domain of the webhook") that apps are told to use directly (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), while the gem's own HMAC verification never binds that value to the signature.

### Title
Webhook shop-domain attribution is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, while `shop` is read from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header. `ShopifyAPI::Webhooks::Registry.process` verifies the HMAC over the body only and then dispatches to the host app's handler with `shop: request.shop` taken straight from that header, so the shop attribution is never bound to the cryptographic signature.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`: [1](#0-0) 

- `hmac` is read from the `hmac-sha256` header.
- `shop` is read from the `shop-domain` header.
- `to_signable_string` returns only `@raw_body`. [1](#0-0) 

`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (the raw body) and compares it to `verifiable_query.hmac`: [2](#0-1) 

`Registry.process` checks this HMAC, then immediately forwards `request.shop` — the unauthenticated header value — to the app-supplied handler as the shop attribution for the event: [3](#0-2) 

The identity binding that should hold is: `bytes verified by HMAC == bytes the shop attribution is derived from`. Here that equality is broken — the HMAC only verifies `raw_body` bytes, never the `shop-domain` header bytes. Any party who can obtain one valid `(raw_body, hmac)` pair for the app's shared `client_secret` (e.g., a malicious merchant who has installed the app themselves and thus legitimately receives real webhooks signed with the app's secret, since `api_secret_key` is per-app, not per-shop) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header naming a victim shop. The signature still validates (it never covered the header), and the gem hands the forged `shop` value straight to the handler.

The library's own documentation instructs developers to trust `data.shop` directly as "The shop domain of the webhook" without any additional verification step, reinforcing that this is the intended, sole point of shop attribution for a processed webhook: [4](#0-3) 

### Impact Explanation
This allows cross-tenant confusion/access: an attacker who is a legitimate (but malicious) installer of the app on their own shop can forge webhook events that the host application will process as belonging to a different, victim shop — because the gem-level verification step (`Registry.process`) never establishes that the signed body actually originated for that `shop` value. Depending on how the host app uses `data.shop` (e.g., to key database writes, cache invalidation, order/customer record updates, background job dispatch as shown in the docs example `perform_later(shop_domain: data.shop, ...)`), this can lead to data being attributed to, or overwritten under, the wrong tenant — a cross-tenant integrity breach mediated entirely by this gem's verification primitive.

### Likelihood Explanation
Exploitability requires only that the attacker be able to install the target app on any shop they control (a standard, low-privilege capability for any merchant), capture one legitimate webhook body+HMAC pair sent to their own endpoint, and replay it with a forged `shop-domain` header to the app's callback route. No knowledge of `api_secret_key` or `client_secret` is needed since the attacker already legitimately receives a validly-signed body/HMAC from Shopify for their own store.

### Recommendation
Include the shop domain (and topic/webhook-id) inside the HMAC-covered signable content, or require the host application to cross-check `request.shop` against a set of shops with known, valid sessions/installations before trusting it in `Registry.process`. At minimum, document prominently that `data.shop` is unauthenticated and must be independently verified by the host app before being used for any tenant-scoped operation.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`, and configures a webhook subscription (e.g. `orders/create`).
2. Shopify sends a real webhook to the attacker's endpoint with a valid `x-shopify-hmac-sha256` computed over the raw body using the app's shared `api_secret_key`, and header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures the exact `raw_body` and `hmac` value.
4. Attacker sends a new HTTP request to the same app webhook endpoint, reusing the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` is built and passed to `ShopifyAPI::Webhooks::Registry.process`, which calls `Utils::HmacValidator.validate(request)` — this passes because it only checks the unchanged `raw_body` against the unchanged `hmac`.
6. The registered handler's `handle(data:)` is invoked with `data.shop == "victim-shop.myshopify.com"`, even though the payload never actually originated from Shopify for that shop, causing the host app to process/attribute the event to the wrong tenant.

### Citations

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```

**File:** docs/usage/webhooks.md (L12-30)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
