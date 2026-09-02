### Title
Webhook `shop-domain` used to bind incoming data to a tenant is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC over the raw request body, then hands the handler a `shop` value that is taken from an HTTP header that is never part of the signed material. This breaks the equality that the caller relies on: `shop` used to key/act on tenant data ≠ `shop` actually covered by the cryptographic signature.

### Finding Description
`Utils::HmacValidator.validate` computes the signature only from `verifiable_query.to_signable_string`. For webhooks, `Request#to_signable_string` returns just `@raw_body`: [1](#0-0) 

The `shop` (and `topic`, `webhook_id`, `api_version`) values are read directly from HTTP headers, which are not included in the HMAC input at all: [2](#0-1) 

`Registry.process` validates only the body HMAC and then immediately forwards `request.shop` to the handler as the tenant identity for the webhook payload: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` confirm only that *some* valid HMAC producer (i.e., anyone who legitimately received a webhook signed with the app's shared secret, such as an attacker who installed the app on their own store) generated the body bytes — it proves nothing about which shop the body is associated with: [4](#0-3) 

Because `shop` is carried out-of-band from the signed content, the binding "shop whose credentials produced this HMAC" == "shop the handler acts on" does not hold: an attacker can take a validly-signed webhook body (from their own shop, or any shop they control/observe) and re-deliver it to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header pointing at a victim shop. The HMAC check still passes (it only checks the body), and `Registry.process` passes the attacker-controlled `shop` value straight to the handler, which typically uses it to look up the victim's stored access token/session and act on the payload as if it originated from the victim's store.

### Impact Explanation
This is a cross-tenant data/action injection: the webhook handler processes attacker-supplied content under the identity of a different, victim shop, because the trust boundary the app relies on (a validated Shopify webhook implies the enclosed `shop` is authentic) is not actually enforced by the gem. This matches the "Critical - cross-tenant access" impact category, since the `shop` field that gates which tenant's session/access token is used is never bound to the authenticated bytes.

### Likelihood Explanation
High. Any entity capable of installing the app on any shop (or otherwise legitimately receiving one authentic webhook payload+HMAC pair, which Shopify computes with the same secret for every shop using the app) can capture a valid `(raw_body, hmac)` pair and replay it against the same public webhook endpoint with a different `shop-domain` header. No access token, `client_secret`, or privileged access is required — only a normal, unprivileged app installation is needed to obtain one legitimate signed payload.

### Recommendation
Include the shop (and ideally topic/webhook id) in the material that is cryptographically bound to the request, or otherwise require the caller to independently verify that `request.shop` corresponds to a shop with an active install/session before trusting it. At minimum, `Utils::HmacValidator`/`Webhooks::Request` should not present `shop` as a validated field of a `process`-checked request when it is excluded from `to_signable_string`; the library should document explicitly that `shop` is unauthenticated and require host apps to cross-check it against known installed shops before use, or extend `to_signable_string` to bind the shop domain into the digest.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, obtaining a legitimately Shopify-signed webhook delivery, e.g. body `{"id":1,...}` with header `X-Shopify-Hmac-Sha256: <valid hmac over body>` and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker resends the exact same body and HMAC header to the app's public webhook endpoint, but replaces `X-Shopify-Shop-Domain` with `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only — this still matches, since the body was untouched: [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop == "victim.myshopify.com"`, even though the payload content and signature originated from the attacker's own shop: [6](#0-5) 
5. A host application that uses `shop` to fetch the victim's stored session/access token and apply the payload will act on attacker-controlled data under the victim's tenant context.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
