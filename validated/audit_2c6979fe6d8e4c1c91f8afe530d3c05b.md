### Title
Webhook `shop-domain` header is trusted for tenant routing but is not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value that is used to route and process a webhook directly from the unauthenticated `X-Shopify-Shop-Domain` HTTP header, while `Utils::HmacValidator.validate` only verifies the HMAC over the raw request body. The identity binding that should hold — `signed_content == acted_upon_shop` — is broken: the byte range that is HMAC-verified (`@raw_body`) does not include the field (`shop-domain` header) that the registry uses to attribute the webhook to a tenant.

### Finding Description
`Request#hmac` and `Request#to_signable_string` only ever operate on `@raw_body`: [1](#0-0) [2](#0-1) 

`shop` is read from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is not part of `to_signable_string` and therefore plays no role in the HMAC computation: [3](#0-2) 

`Registry.process` validates the HMAC (which only covers the body) and then unconditionally trusts `request.shop` and forwards it, unmodified, to the app's handler as the tenant identity for the event: [4](#0-3) 

Because the gem's shared `Context.api_secret_key` is the same for every shop that installs a given app (Shopify apps have one `client_secret`, not one secret per shop), any merchant that legitimately installs the app receives real webhooks with a valid HMAC computed over the body with that same secret. Such a merchant (an "unprivileged internet user" with respect to any other tenant of the app) can replay that body to the app's webhook endpoint while substituting a different value in the `X-Shopify-Shop-Domain` header. `HmacValidator.validate` will still pass because the header is never part of the signed content, and `Registry.process` will hand the forged `shop` value straight to the app's handler as if the event genuinely originated from another tenant — a cross-tenant confusion/spoofing primitive that requires no access token, no `client_secret`, and no host application misbehavior; it results purely from this gem's own signature scope.

### Impact Explanation
This crosses the "cross-tenant access" bar: a store owner with legitimate, low-privilege access to the app (their own webhook deliveries) can make the app's webhook handler process an event while believing it came from a different shop, since `shop` is the only tenant-identifying value passed to `WebhookMetadata` and it is not authenticated. Any handler logic keyed off `data.shop` (e.g., looking up per-shop credentials, applying per-shop side effects, invoking GDPR redact flows for `shop/redact`) is exposed to this confusion.

### Likelihood Explanation
Exploitation requires only: (1) being a legitimate merchant able to install the target app and receive at least one real webhook (to obtain a validly-signed body/HMAC pair), and (2) the ability to send an arbitrary HTTP request with attacker-chosen headers to the app's public webhook endpoint. Both conditions are met by any unprivileged internet user who installs the app once. No secrets need to be extracted.

### Recommendation
Bind the shop identity into the verified content instead of trusting an unauthenticated header: include the `shop-domain` (and ideally `topic`/`webhook-id`) header value in `to_signable_string`, or require the caller/registry to independently authenticate the shop-to-secret relationship (e.g. per-shop signing verification) before dispatching to `handler.handle`. At minimum, document that `request.shop` must not be treated as authenticated in `Registry.process` and require handlers to cross-check it against an out-of-band trusted mapping before use.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com`; attacker receives a genuine webhook POST with header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, a JSON body, and `X-Shopify-Hmac-Sha256` computed by Shopify over that body using the app's single `client_secret`.
2. Attacker resends the identical body and HMAC header to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`@raw_body`, unchanged) — validation succeeds. [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`, even though the payload/HMAC never originated from or was bound to that shop.

### Citations

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
