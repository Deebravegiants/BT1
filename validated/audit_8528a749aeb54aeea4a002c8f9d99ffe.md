This confirms the finding: the webhook `hmac` signature only covers `@raw_body` (the request body), while the `shop-domain` header is read separately and never included in the signed data, yet `Registry.process` trusts `request.shop` as the tenant identity passed straight to the handler. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook HMAC only signs the request body, leaving the `shop-domain` header unauthenticated, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC signature validated by `ShopifyAPI::Utils::HmacValidator.validate` never covers the `shop-domain` (or `topic`/`webhook-id`/`api-version`) headers. `ShopifyAPI::Webhooks::Registry.process` accepts any request whose body HMAC checks out and then unconditionally forwards `request.shop` (parsed straight from the unauthenticated header) to the app's webhook handler as the tenant identity. This breaks the intended binding: `shop-domain header == HMAC-authenticated shop`.

### Finding Description
`Request#hmac` decodes the `hmac-sha256` header and `Request#to_signable_string` returns `@raw_body` only:
```ruby
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end
...
def to_signable_string
  @raw_body
end
```
`shop`, `topic`, `webhook_id`, and `api_version` are all read from headers that are never fed into `to_signable_string`, so they are not covered by the HMAC computation in `HmacValidator.validate_signature`, which only signs `verifiable_query.to_signable_string` (the body). `Registry.process` performs:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
```
Because the HMAC check succeeds purely based on the body matching the app's `api_secret_key`, any request carrying a body/HMAC pair that is valid for *some* shop (e.g., the attacker's own store, which legitimately receives real signed webhooks from Shopify for topics like `orders/create`) can have its `shop-domain` header rewritten to an arbitrary victim shop domain, and `Registry.process` will still accept it and hand the forged shop identity to the app's handler unchanged.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who operates their own Shopify store (an unprivileged internet user with no special access to the target) can capture one of their own legitimately-signed webhook deliveries and replay it against the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to any victim shop's domain. Any consuming application that trusts `WebhookMetadata#shop` (as the gem's own documentation instructs: "`shop`, `String` - The shop domain of the webhook") for authorization or data routing decisions (e.g., looking up the victim's session/access token, updating victim shop data, deduplication keyed by shop) will act on attacker-supplied data believing it originates from the victim shop, since the gem provides no way to verify the header is authentic.

### Likelihood Explanation
High likelihood: the attacker only needs their own installed app instance (freely obtainable, since any developer/merchant can install a public app or expose their own dev store) to obtain a validly-HMAC-signed webhook body, then can trivially manipulate the unsigned header before delivery to the app's webhook endpoint. No access to `api_secret_key`, tokens, or the victim's environment is required.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in the signable string used for HMAC validation, or otherwise cryptographically bind the shop claim to the signed payload before `Registry.process` exposes `request.shop` to handlers. At minimum, document/require that consumers independently verify `request.shop` corresponds to a shop for which they have an active, previously-established session/installation record rather than trusting the header outright.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. body `{"id":1}` with header `X-Shopify-Hmac-Sha256: <valid-hmac-for-body>` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker replays this exact HTTP request to the app's webhook endpoint but changes only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only validates `@raw_body` against the shared `api_secret_key` — the header change has no effect on the check. [4](#0-3) 
4. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` with `shop == "victim-shop.myshopify.com"`, even though Shopify never issued that webhook for that shop. [5](#0-4) 
5. The app's handler processes attacker-controlled body data under the identity of `victim-shop.myshopify.com`, exactly as documented in `docs/usage/webhooks.md` (`data.shop` is described as "the shop domain of the webhook").

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
