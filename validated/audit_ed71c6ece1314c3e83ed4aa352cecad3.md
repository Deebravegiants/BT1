### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body, then trusts the `shop` (and other) headers — which are never included in the signed payload — to attribute the delivery to a specific merchant.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the signature only against `verifiable_query.to_signable_string`. For webhook requests, `Request#to_signable_string` returns just `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are pulled straight from unauthenticated HTTP headers, independent of the signed body: [2](#0-1) 

`Registry.process` validates only the HMAC, then immediately hands `request.shop` (an unsigned field) to the registered handler as the tenant identifier for the payload: [3](#0-2) 

This is exactly the bug class from the external report generalized to this gem's HMAC-verification boundary: the check ("is this body's HMAC valid for `api_secret_key`?") answers a narrower question than the one the code actually relies on ("did this exact `(shop, topic, body)` tuple come from Shopify for this shop?"). The equality that should hold is:

`verified(request) == { body, shop_that_produced_this_hmac }`

but what the code actually enforces is:

`verified(request) == { body }`, while `data.shop = request.header("shop-domain")` is asserted, not verified.

Because a single `api_secret_key` is shared across every shop that has installed the app, any merchant who has legitimately installed the app receives real webhook deliveries with a valid `(body, hmac)` pair signed under that shared secret. That merchant (an unprivileged, non-admin actor from the perspective of any *other* tenant of the app) can resend that exact body/HMAC pair to the app's webhook endpoint while altering only the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header to point at a victim shop. `Registry.process` will still report `Utils::HmacValidator.validate` as `true` (it only checked the body) and will dispatch `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: attacker_body, ...)` to the app's handler, which typically uses `shop` to look up the tenant's session/data record and apply the payload.

### Impact Explanation
This lets a merchant who is a legitimate, but unprivileged (relative to other tenants), user of a multi-tenant app attribute arbitrary attacker-chosen webhook bodies to a different tenant (victim shop), because the tenant-identifying field is never covered by the cryptographic signature. Depending on the handler's logic (e.g., `app/uninstalled`, `customers/data_request`, `orders/create`), this can result in cross-tenant data corruption/injection or forged lifecycle events being applied to a shop the attacker doesn't own — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Requires the attacker to already be an installed, but otherwise unprivileged, merchant of the target app so they can obtain at least one valid `(body, hmac)` pair signed with the app's shared `api_secret_key`; no access to `api_secret_key`, tokens, or admin credentials is needed. The header can then be freely rewritten before delivery to the app's callback endpoint.

### Recommendation
Bind the tenant-identifying fields into the signed payload (or otherwise cryptographically bind them), e.g. by including `shop`, `topic`, and `webhook_id` in the string that is HMAC-verified, or by requiring the host application to cross-check `request.shop` against an expected/allow-listed shop for the delivery before processing. At minimum, document prominently that `Webhooks::Registry.process` does not authenticate the `shop` header, and require callers to independently verify shop identity (e.g., against a known installed-shop list) before trusting `WebhookMetadata#shop`.

### Proof of Concept
1. App has two tenants, `shop-a.myshopify.com` (attacker-controlled) and `shop-b.myshopify.com` (victim), sharing one `api_secret_key`.
2. Shopify sends a real webhook to the app for `shop-a`: body `B`, header `X-Shopify-Shop-Domain: shop-a.myshopify.com`, and `X-Shopify-Hmac-Sha256: HMAC(secret, B)`.
3. Attacker (who controls `shop-a`'s server/proxy or intercepts their own inbound webhook) re-POSTs the same raw body `B` and same HMAC header to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain` to `shop-b.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks the body against the HMAC.
5. `Registry.process` dispatches `WebhookMetadata.new(shop: "shop-b.myshopify.com", body: B, ...)` to the handler, which acts on victim shop `shop-b` using attacker-controlled body `B`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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
