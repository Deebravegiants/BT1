## Title
Webhook `shop` identity is trusted without HMAC coverage, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (and `topic`) values are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then hands the *unauthenticated* `shop` value straight to the app's webhook handler. Any actor who can obtain one genuinely-signed webhook payload (e.g. by installing the app on their own store) can replay that exact body with a forged `X-Shopify-Shop-Domain` header pointing at a victim shop, and the HMAC check still passes, causing the handler to process attacker-controlled webhook data as if it belonged to a different tenant.

### Finding Description
`Utils::VerifiableQuery` requires each verifiable object to expose `hmac` and `to_signable_string`, and `HmacValidator.validate` recomputes the HMAC purely over `to_signable_string` using the app's shared `api_secret_key`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw HTTP body — it does not include the shop domain: [2](#0-1) [3](#0-2) 

`Registry.process` validates that HMAC and then passes `request.shop` — sourced solely from the `shopify-shop-domain`/`x-shopify-shop-domain` header — into the handler's metadata without any additional binding to the signed content: [4](#0-3) 

Because Shopify signs webhooks to a given app using that app's single shared secret regardless of which installed shop originated the event, any shop that has legitimately installed the app can capture a real, validly-signed `(body, hmac)` pair from its own webhook deliveries. That pair remains valid for *any* value of the `shop-domain` header, since the header is never part of the signed string. The attacker can then send that same `(body, hmac)` to the app's webhook endpoint with the header rewritten to name a victim shop.

The broken identity binding is:
```
shop authenticated by HMAC  !=  shop delivered to the handler (request.shop)
```
`HmacValidator.validate(request)` proves only that "this body was signed by our secret", never that "this body originated from `request.shop`".

### Impact Explanation
This breaks the tenant boundary the host application relies on: `WebhookMetadata#shop` is the field host apps (e.g. via `ShopifyApp`) use to look up the target shop's session/access token and to attribute/persist webhook data. An attacker-controlled shop can forge webhook events "from" an arbitrary victim shop domain, since the shop string is fully attacker-supplied and unauthenticated, while the payload only needs to be *any* real signed body the attacker can generate for their own store. This is a cross-tenant confusion vulnerability — Critical per the ruleset's "cross-tenant access" category — because a shop the attacker legitimately controls can inject events attributed to shops it does not control.

### Likelihood Explanation
Any developer or malicious actor can install the target app on their own Shopify development store (unprivileged with respect to any other merchant) and receive real signed webhooks. Capturing one such `(raw_body, hmac)` pair and replaying it with a different `shop-domain` header requires no secrets beyond passive observation of one's own webhook traffic, making this trivially exploitable by any app-installing party.

### Recommendation
Include the shop identifier as part of the signed content verified by `HmacValidator`, or otherwise cryptographically bind the `shop` header value to the signature before trusting it, e.g. Shopify's platform-side webhook payload already embeds tenant context inside the body itself for many topics — the gem should not treat `request.shop` (a bare header) as authenticated just because the (unrelated) body HMAC passed. At minimum, document/require host apps to cross-check `request.shop` against the previously known shop for that webhook subscription/session rather than treating it as self-authenticating, or extend `to_signable_string` (and Shopify's signing contract) to cover the shop domain.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and registers a webhook via `ShopifyAPI::Webhooks::Registry`.
2. Shopify delivers a legitimately HMAC-signed webhook to the app's endpoint: headers include `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, plus the raw JSON body.
3. Attacker resends the identical raw body and identical HMAC header to the same endpoint, but replaces `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `to_signable_string` (`@raw_body` only) — it matches, since the body and secret are unchanged: [4](#0-3) 
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker-controlled>, ...)`, processing attacker data as if `victim-shop.myshopify.com` sent it.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
