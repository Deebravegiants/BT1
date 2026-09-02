## Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing shop-domain spoofing with a genuine signature - (File: `lib/shopify_api/webhooks/request.rb`)

## Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` attribute that the handler receives and trusts as the tenant identity is taken from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never included in the HMAC-signed material. Anyone who can obtain one genuine, validly-signed webhook body (e.g. because they operate their own shop with the app installed) can resend that exact body to the app's webhook endpoint while substituting an arbitrary `shop-domain` header, and the signature will still validate because the app-wide `client_secret` (not a per-shop secret) is what signs the body, independent of the shop field.

## Finding Description
`ShopifyAPI::Webhooks::Request` builds its authenticated payload from only the raw body:

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

`shop` is read independently from a header that is not part of that signable string:

```ruby
sig { returns(String) }
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [2](#0-1) 

`Registry.process` validates the HMAC and then dispatches to the handler using this unauthenticated `shop`:

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [3](#0-2) 

`Utils::HmacValidator.validate` signs with `Context.api_secret_key`, which is the single application `client_secret` shared across every merchant/tenant that has this app installed — it is not a per-shop secret:

```ruby
def validate(verifiable_query)
  return false unless verifiable_query.hmac
  result = validate_signature(verifiable_query, Context.api_secret_key)
  ...
end
``` [4](#0-3) 

The identity binding that should hold is:

`shop authenticated (bytes covered by the HMAC) == shop delivered to the handler as the tenant identity`

Here, the `shop` value delivered to `WebhookMetadata` is **not** covered by the HMAC — only `@raw_body` is. Because the signing key (`client_secret`) is identical for every shop using the same app installation, an unprivileged user who controls one tenant (their own shop, with the app legitimately installed) can capture a genuine webhook delivery for their own shop and replay the identical body with a forged `shopify-shop-domain` header pointing at a victim shop. The HMAC still validates (same secret, same body), and `Registry.process` passes the forged `shop` straight to the application's handler as if it were an authentic event for the victim tenant.

## Impact Explanation
Since host applications built on this gem typically use the `shop` field from `WebhookMetadata` to select which merchant/tenant record to update (e.g., writing order/customer/inventory data keyed by shop), an attacker can inject data attributed to another tenant, achieving cross-tenant data confusion/injection with a validly-signed request. This matches the Critical "cross-tenant access" impact category, since the tenant boundary is enforced only by an unauthenticated header value.

## Likelihood Explanation
Likelihood is Medium: the attacker needs their own real installation of the target app (to receive genuine webhook deliveries with valid HMACs) and the ability to send arbitrary HTTP requests to the app's public webhook endpoint — both of which any unprivileged merchant/user of a public app can obtain without any secret, token, or privileged access.

## Recommendation
Bind the `shop` (and other trust-relevant fields like `topic`/`api_version`/`webhook-id`) into the value that is verified, or otherwise cross-check the header-derived `shop` against an independently trusted source before dispatching to handlers — for example, include the `shop-domain` header in `to_signable_string`, or require host applications to confirm that `request.shop` matches a shop for which they expected/registered the webhook, rejecting mismatches in `Registry.process` itself rather than leaving this entirely to downstream handler code.

## Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with body `B` and header `shopify-hmac-sha256: H`, where `H = HMAC_SHA256(client_secret, B)` per `HmacValidator.validate_signature` / `compute_signature`. [5](#0-4) 
2. Attacker resends the exact same raw body `B` and header `H` to the app's public webhook endpoint, but replaces `shopify-shop-domain: attacker.myshopify.com` with `shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (no header content is checked against the signature) [6](#0-5) , `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only hashes `@raw_body` [7](#0-6) .
4. The application's handler receives `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: parsed_body, ...)` and processes attacker-controlled order data as if it originated from `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-40)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
        end
```
