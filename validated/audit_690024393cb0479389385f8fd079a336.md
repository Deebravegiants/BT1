Based on my investigation, the strongest reachable analog is in the webhook processing path: the HMAC only signs the raw body, while the `shop-domain` header is trusted as the tenant identity without being covered by that signature.### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing in `Webhooks::Registry.process` - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [1](#0-0) , so `Utils::HmacValidator.validate` proves only that the *body bytes* were signed with the app's secret [2](#0-1) . The tenant identity used downstream, `request.shop`, is read straight from the `x-shopify-shop-domain` / `shopify-shop-domain` header and is never included in the signed material [3](#0-2) . `Registry.process` validates the HMAC and then hands `request.shop` straight to the host app's handler as the authoritative tenant identifier, with no cross-check against anything bound by the signature [4](#0-3) .

### Finding Description
The equality that should hold is:

`shop bound by HMAC == shop used to attribute/process the webhook`

In `Webhooks::Request`, the HMAC is verified against `to_signable_string`, which is defined as just `@raw_body` [1](#0-0) . The `shop` accessor, however, is derived from a header that plays no part in that signable string [3](#0-2) [5](#0-4) .

`Registry.process` does:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [4](#0-3) 

`WebhookMetadata#shop` is a plain `String` const with no further validation [6](#0-5) . There is nothing in this gem's code path that checks `request.shop` is the shop that actually owns/signed the body — the HMAC only proves the *body* is authentic Shopify content for *some* shop using this app's secret, not that the accompanying `shop-domain` header matches that shop.

This is directly analogous to the reported bug class: a value ("the shop identity") is acted upon by the library and passed downstream as trusted, while the field carrying it is not covered by the same cryptographic check (HMAC) that is used to establish trust for the rest of the payload — mirroring "a shop authenticated versus the shop stored as a session key" / "a field acted on but not covered by the HMAC" in the rules.

### Impact Explanation
Any merchant that has installed the app (an unprivileged internet user with respect to *other* merchants' tenants) receives their own genuine, correctly-HMAC-signed webhook deliveries from Shopify. Because the signature covers only the body, that exact `(body, hmac)` pair remains valid regardless of which `x-shopify-shop-domain` header accompanies it. The attacker can replay the captured request to the app's webhook endpoint while substituting a victim shop's domain in the header. `Utils::HmacValidator.validate` still returns `true` (the body/HMAC pair is legitimate), and `Registry.process` forwards `shop: <victim-shop>` to the host app's handler as if the event had come from the victim's store [4](#0-3) . If the host application uses `WebhookMetadata#shop` as a tenant/session key (a documented, expected usage pattern of this gem — the class exists specifically to hand shop identity to handlers), this results in cross-tenant data confusion/injection: an attacker can cause data attributed to their own shop's webhook body to be processed and stored under a victim shop's tenant key, or trigger tenant-scoped side effects (e.g., order/customer record updates) against a shop the attacker does not control. This satisfies the "cross-tenant access" criterion for Critical impact.

### Likelihood Explanation
Likelihood is significant: no secret, access token, or privileged access is required — only that the attacker themselves has (or can obtain via a free/development store) a legitimate installation of the target app, allowing them to harvest a valid `(body, hmac)` pair for replay with an arbitrary shop header. The gem performs no additional binding between the signed body and the header-derived shop, so exploitation depends solely on network-level ability to POST to the app's public webhook endpoint with attacker-chosen headers, which is trivial for any internet user.

### Recommendation
Bind the shop identity into the HMAC-verified material, or otherwise cryptographically tie `request.shop` to the signed body:
- Include `shop-domain` (and ideally `topic`, `webhook-id`) in `to_signable_string`, or
- After HMAC validation, independently verify the `shop` header value via a separate authenticated channel (e.g., cross-check against an actively stored session/access token registered for that shop before trusting the header), and
- Document clearly that `WebhookMetadata#shop` is not covered by the HMAC so host applications do not treat it as fully trusted without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own development/free store `attacker-shop.myshopify.com`.
2. Shopify delivers a legitimate webhook, e.g. `orders/create`, to the app's endpoint with headers:
   - `x-shopify-hmac-sha256: <valid HMAC over raw body>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - raw body: `{"id": 1, ...}`
3. Attacker captures this exact HTTP request (raw body + HMAC header untouched).
4. Attacker resends this request to the app's webhook endpoint, changing only:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (`@raw_body`, unchanged) and returns `true` [1](#0-0) [7](#0-6) .
6. `handler.handle` is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` [8](#0-7) , causing the host application to process attacker-controlled data under the victim tenant's identity.

Note: this finding relies on the assumption (consistent with Shopify's documented webhook signing scheme) that the host application uses `WebhookMetadata#shop` from this gem as an authoritative tenant key without independent re-verification — I could not fully verify how the various downstream `shopify_app`/host integrations consume this field since that code lives outside this gem's index.

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
