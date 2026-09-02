This confirms the finding: for webhook processing, `Utils::HmacValidator.validate(request)` only verifies the raw HTTP body against the HMAC signature — `Webhooks::Request#to_signable_string` returns only `@raw_body`, at [1](#0-0) . The `shop`, `topic`, and `webhook_id` fields used downstream are read directly from HTTP headers, which are never part of the signed payload, at [2](#0-1) . `Registry.process` validates the HMAC and then trusts `request.topic`, `request.shop`, and `request.webhook_id` to build `WebhookMetadata` passed to the app's handler, at [3](#0-2) .

### Title
Webhook HMAC validation covers only the request body, not the `shop-domain`/`topic` headers, allowing shop/topic spoofing in verified webhooks - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, so the HMAC-SHA256 signature verified by `Utils::HmacValidator.validate` never covers the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, or `X-Shopify-Webhook-Id` headers. Any of these headers can be freely modified by whoever delivers the HTTP request to the app's webhook endpoint without invalidating the signature, because the signature is computed over the body alone (matching Shopify's actual webhook signing scheme, but leaving header trust entirely up to the host app / network layer).

### Finding Description
`Webhooks::Registry.process` is the gem's sanctioned entry point for handling inbound webhooks:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
end
```
`Utils::HmacValidator.validate` recomputes the HMAC over `verifiable_query.to_signable_string` and compares it to `verifiable_query.hmac`. For `Webhooks::Request`, `to_signable_string` is `@raw_body` — the header-derived `shop`, `topic`, and `webhook_id` accessors are not part of the signed string at all. This breaks the identity binding: `HMAC(secret, body) == received_hmac` is verified, but the code then trusts `shop == header["shopify-shop-domain"]` as if it were authenticated, when in fact `shop` was never bound to the signature.

Any party capable of sending an HTTP request with a valid `(body, hmac)` pair for one shop (e.g., replaying a legitimate webhook delivery, or an intermediary/proxy that can alter headers in transit before the request reaches the app) can substitute an arbitrary `shop-domain` header while keeping the same body and HMAC, and the check will still pass — because the HMAC never depended on the shop header to begin with.

### Impact Explanation
This affects cross-tenant data attribution: a webhook handler using `WebhookMetadata#shop` to route or store the payload against a merchant's tenant record could process a legitimate payload (or an unrelated body it also has a valid signature for, e.g., mandatory compliance topics reused across shops) under an attacker-chosen shop identity. Whether this rises to "cross-tenant access" depends entirely on how the host app uses `request.shop`/`data.shop`, and this gem does not fetch or leak credentials itself — the attacker needs an interception/replay position to alter headers of an otherwise-genuine Shopify-signed delivery, which is a narrower prerequisite than a full authentication bypass.

### Likelihood Explanation
Low-to-moderate. It requires the attacker to already possess or intercept a validly-signed `(body, hmac)` pair, or convince Shopify to deliver a signed payload with attacker-controllable shop context (e.g., mandatory GDPR topics where an attacker's own dev shop generates a legitimate signature over a body they can then replay elsewhere with a modified shop header, if the delivery path passes through a place they control before reaching the app).

### Recommendation
Bind the shop domain (and ideally topic/webhook-id) into the signed material actually verified, or independently validate `request.shop` against the shop associated with the session/tenant expected to receive that topic before trusting it in `WebhookMetadata`. At minimum, document that `Webhooks::Request#shop`/`#topic` are **not** cryptographically bound by the HMAC check and must not be treated as verified identity by consuming applications.

### Proof of Concept
```ruby
raw_body = '{"id":123}'
secret = ShopifyAPI::Context.api_secret_key
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, raw_body)

# Legitimate delivery for shop-a
headers_a = {
  "shopify-topic" => "orders/create",
  "shopify-hmac-sha256" => Base64.encode64(hmac),
  "shopify-shop-domain" => "shop-a.myshopify.com",
}

# Attacker-modified delivery, same body/hmac, different shop header
headers_b = headers_a.merge("shopify-shop-domain" => "shop-b.myshopify.com")

req = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers_b)
ShopifyAPI::Utils::HmacValidator.validate(req) # => true, even though shop header was altered
``` [4](#0-3) [3](#0-2) [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
