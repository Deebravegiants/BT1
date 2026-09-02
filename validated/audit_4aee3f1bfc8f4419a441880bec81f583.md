Based on my investigation, I found a valid analog vulnerability in the webhook processing flow.

### Title
Webhook shop domain is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the **raw request body**, while the `shop` value that identifies *which tenant* the webhook belongs to is taken from an HTTP header that is never included in the signed bytes. An attacker who can obtain one validly-signed webhook delivery (e.g., because they operate their own shop with the app installed) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting the `shop-domain` header for a different, victim shop.

### Finding Description
`HmacValidator.validate` computes the HMAC only over `verifiable_query.to_signable_string`, and for webhooks that method returns just `@raw_body`: [1](#0-0) 

The `shop` (tenant identity), `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers that are **not part of the signable string**: [2](#0-1) 

`Registry.process` validates only the HMAC of the body and then immediately trusts `request.shop` as the tenant identity passed to the app's handler: [3](#0-2) 

This breaks the intended binding: `bytes verified (raw_body + secret)` should equal `bytes that determine tenant identity (shop header)`. Instead, `bytes verified != bytes that determine tenant`. The library's own documentation instructs consumers to trust `data.shop` from the callback as the authoritative tenant for that webhook, with no additional check that the shop is bound to the signature: [4](#0-3) 

Since a single app uses one shared `api_secret_key` for **all** installed shops, any shop that has installed the app can obtain a validly HMAC-signed `(body, hmac)` pair from a real webhook delivery to itself (many topics, e.g. `app/uninstalled`, GDPR redact topics, or any topic with a small/predictable/empty JSON body, produce identical or attacker-influenceable bodies). The attacker then POSTs that same `raw_body`/HMAC directly to the app's public webhook URL (this endpoint is just an ordinary HTTP route on the merchant-facing server, reachable by anyone, not only by Shopify's IPs, since this gem performs no origin/IP check) with the `shopify-shop-domain` header changed to the victim shop. `HmacValidator.validate` succeeds because it only checks the body bytes, and `Registry.process` calls the handler with `shop: request.shop` set to the attacker-chosen victim domain, causing the host application to act on the victim tenant's data with an attacker-controlled body.

### Impact Explanation
This crosses a tenant boundary: an attacker who is a legitimate customer of the app (having installed it into their own shop) can trigger the app's webhook handler to execute logic for a *different* merchant's shop using a validly-authenticated request, since only the body — not the tenant-identifying shop — is bound by the HMAC. Depending on the handler, this can lead to unauthorized cross-tenant actions such as spoofing `app/uninstalled` to trigger cleanup/deauthorization for another tenant, or spoofing GDPR redact/data-request webhooks against another shop's data. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Requires an attacker to have (or acquire) a shop with the target app installed to legitimately receive one signed webhook — a low bar for any public app since installing an app typically requires no special privilege beyond having a Shopify store. No possession of the `api_secret_key` itself is required, only a captured, validly-signed body/HMAC pair coupled with the ability to send arbitrary HTTP requests (with arbitrary headers) directly to the app's webhook endpoint.

### Recommendation
Bind the tenant-identifying fields (`shop`, and ideally `topic`/`webhook_id`) into the signed material verified by `HmacValidator`, or independently verify that the shop domain in the header corresponds to a shop with an active, known installation before trusting it, rather than relying purely on body-only HMAC verification combined with an unauthenticated header.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, receiving a legitimately signed webhook, e.g. topic `app/uninstalled` with body `{}` and header `shopify-hmac-sha256: <valid HMAC over "{}">`.
2. Attacker sends a POST request directly to the app's public webhook endpoint with:
   - Body: `{}`
   - Header `shopify-hmac-sha256`: the captured valid HMAC
   - Header `shopify-shop-domain`: `victim.myshopify.com` (spoofed)
   - Header `shopify-topic`: `app/uninstalled`
3. `ShopifyAPI::Webhooks::Registry.process` calls `HmacValidator.validate`, which succeeds because the body `{}` matches the signed body.
4. The registered handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: "app/uninstalled", body: {})`, causing the host app to process an uninstall/deauthorization action for `victim.myshopify.com` despite no such event having occurred for that shop.

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

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
