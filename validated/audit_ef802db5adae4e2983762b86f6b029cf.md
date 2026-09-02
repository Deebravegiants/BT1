### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (tenant) identity from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature that `ShopifyAPI::Utils::HmacValidator` verifies only covers the raw request body. Any unprivileged actor who can obtain one valid `(raw_body, hmac)` pair — trivially available by installing the target app on their own store and receiving a legitimate webhook — can replay that exact body/HMAC pair while substituting an arbitrary victim shop domain in the header. `Registry.process` accepts the request as valid and hands the handler a `WebhookMetadata` object whose `shop` field is attacker-controlled, even though the cryptographic check passed.

### Finding Description
The identity binding that should hold is:
`shop asserted to the handler == shop actually authenticated by Shopify's HMAC`

In this gem that equality is broken:

- `Request#hmac` reads only the `hmac-sha256` header [1](#0-0) 
- `Request#shop` reads the `shop-domain` header, entirely separate from the signed material [2](#0-1) 
- `Request#to_signable_string` — the data that is actually HMAC-verified — is just the raw body, and does not include the shop, topic, or webhook-id headers [3](#0-2) 
- `HmacValidator.validate` computes the signature strictly over `to_signable_string` (i.e., the body) and compares it to the received `hmac` [4](#0-3) 
- `Registry.process` trusts this HMAC check as the sole authenticity gate, then immediately forwards `request.shop` (an unauthenticated header value) to the app's handler as the tenant identity [5](#0-4) 

Because `shop` never enters the signable string, the HMAC check answers "was this body signed by our secret" but the code (and the app built on top of it) treats a passing check as also answering "…and for shop X", which is never verified. An attacker who is themselves a legitimately installed merchant (fully unprivileged — no leaked secrets, no privileged account, no TLS interception) receives real Shopify-signed webhooks for their own store. Each such webhook is a valid `(raw_body, hmac)` pair. By re-POSTing that same body/HMAC to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header changed to any victim shop domain, the request still passes `HmacValidator.validate`, and `WebhookMetadata.shop` is populated with the attacker-chosen victim domain.

### Impact Explanation
This breaks the tenant/shop identity binding at the point the gem hands data to the app's webhook handler, which is exactly the kind of cross-tenant identity-binding failure in scope. Any app that keys per-tenant behavior off `WebhookMetadata#shop` (e.g. deciding which shop's data record to update/delete for `customers/data_request`, `customers/redact`, `shop/redact`, `orders/*`, `app/uninstalled`, etc., all standard, expected usages per the gem's own docs) can be tricked into applying attacker-supplied webhook content to a shop the attacker does not control — a cross-tenant access impact reachable by any unprivileged internet user who is simply able to install the app once on a store they control.

### Likelihood Explanation
Likelihood is high for any app relying on this library's documented `Webhooks::Registry.process`/`WebhookMetadata` flow: obtaining a valid `(body, hmac)` pair requires nothing more than installing the target app on an attacker-owned/free trial shop and capturing one inbound webhook POST to the app's own publicly reachable endpoint (the attacker is the recipient's operator, so capturing it needs no interception of anyone else's traffic). Re-sending that request with a modified `Shop-Domain` header requires no cryptographic knowledge, secret, or privileged credential.

### Recommendation
Bind the shop identity into the verified signature material, or otherwise cryptographically tie the `shop`/`topic`/`webhook-id` headers to the payload, e.g., by having `Request#to_signable_string` include the shop domain (matching how `AuthQuery#to_signable_string` correctly includes `shop` in its signed string, see [6](#0-5) ), or require the caller to independently corroborate `request.shop` against a known/installed shop record before trusting it in `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (fully unprivileged, self-service).
2. Shopify delivers a legitimate webhook to the app's public endpoint:
   ```
   POST /webhooks
   X-Shopify-Topic: customers/redact
   X-Shopify-Hmac-Sha256: <valid HMAC of BODY>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   Body: {"customer": {...}}
   ```
   The attacker (operating their own store/app instance, or simply logging their own endpoint) records `BODY` and its valid `X-Shopify-Hmac-Sha256`.
3. Attacker re-sends the identical `BODY` and `X-Shopify-Hmac-Sha256` to the same endpoint, but sets:
   ```
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   ```
4. `HmacValidator.validate` recomputes the HMAC over `BODY` only (per `Request#to_signable_string`) and it matches — the request is accepted.
5. `Registry.process` invokes the handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, an identity never checked by the cryptographic signature, letting the attacker's payload be processed as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
